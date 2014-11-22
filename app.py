from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func, distinct
import model
import search
import numpy
# import lookuptable

#### IT'S HCPCS

app = Flask(__name__)
app.secret_key = 'askjdfiwbueryqaowijfmcw037u41ojmpq9uqije12jnedmp2oq09ef0ccjwo'

PUNCTUATION = '!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/search_results")
def search_results():
	"""Displays a list of doctors matching a speciality in a zipcode (eventually)"""
	# change this later to be specialty. Get speciality as a dropdown menu??
	zipcode = request.args.get("zipcode")
	search_terms = request.args.get("search-terms")

	session = model.connect()

	query = session.query(model.Provider).distinct()

	base_avg = None
	hcpcs_code = None

	# check if user entered anything
	if zipcode == '' and search_terms== '':
		return "Please enter a value"

	else:
		# if user entered a specialty
		if search_terms != '':
			search_terms = ''.join([c for c in search_terms if c not in PUNCTUATION])
			specialties = search.specialty(search_terms)
			codes = search.procedure(search_terms)
			if specialties:
				query = query.filter(model.Provider.specialty.in_(specialties))
				#### maybe rethink this!!!
				base_avg = calc_base_avg(specialties = specialties)
				q1 = query.filter(model.Provider.specialty.in_(specialties))
				if not codes:
					query = q1

			if codes:
				npis = session.query(model.Claim.npi).filter(model.Claim.hcpcs_code == 99233).all()
	 			q2 = query.filter(model.Provider.npi.in_([npi[0] for npi in npis]))
	 			if not specialties:
	 				query = q2
	 			else:
	 				query = q1.union(q2)

		# if user entered a zipcode 
		if zipcode != '':
			query = query.filter(model.Provider.short_zip == int(zipcode[:5]))

		# if user entered a procedure name
		# OLD STUFF
		# if procedure != '':
		# 	procedure = ''.join([c for c in procedure if c not in PUNCTUATION])
		# 	# procedure_codes = lookuptable.procedure_dict[procedure]
		# 	procedures = session.query(model.Claim).\
		# 	join(model.ClaimLookup, model.Claim.hcpcs_code==model.ClaimLookup.hcpcs_code).\
		# 	join(model.ProcSearchTerm).filter(model.ProcSearchTerm.word == procedure).all()
		# 	codes = [procedure.hcpcs_code for procedure in procedures]
		# 	query = query.join(model.Claim).filter(model.Claim.hcpcs_code.in_(codes))
			
			###### TESTING CODE #######
			# string = ' '.join(str(procedure_codes))
			# return string

	# run the query
	doctor_list = query.limit(20).all()
	npi_list = [doctor.npi for doctor in doctor_list]
	# print "/n/n ************ the npi list: ", npi_list," \n\n"
	if doctor_list == []:
		return "No providers match your search! Try searching without a zip code."

	# check to see if base average has already been calculated, if not:
	# calculate the average based on all the claims from all the doctors.
	if base_avg == None:
		base_avg = calc_base_avg(doctor_list = doctor_list)

	# calculate average claim proce for each doctor, maybe with treatment code
	avg_claim_amts = [doctor.priciness(hcpcs_code) for doctor in doctor_list]

	# put that into a numpy array, then calculate standard dev and zscore
	avg_claim_array = numpy.array(avg_claim_amts)
	stdev = numpy.std(avg_claim_array)
	mean = numpy.mean(avg_claim_array)
	for dr in doctor_list:
		zscore = (dr.avg - mean)/stdev
		if zscore <= -2:
			dr.dollars = "$"
		elif zscore <= -1:
			dr.dollars = "$$"
		elif zscore < 1:
			dr.dollars = "$$$"
		elif zscore < 2:
			dr.dollars = "$$$$"
		else:
			dr.dollars = "$$$$$"



	# EARLIER VERSION
	# calculate the average claim price for each doctor, optionally with code
	# for doctor in doctor_list:
	# 	dr_avg = doctor.priciness(hcpcs_code)
	# 	doctor.rel_cost = ((dr_avg - base_avg)/base_avg)*100

	return render_template('search_results.html', doctor_list = doctor_list)

def calc_base_avg(hcpcs_code=None, doctor_list=None, specialties=None):
	"""With either a treatment code or a list of providers, calculate the 
	average submitted charge across all claims of same type or all doctors in 
	the list."""

	session = model.connect()

	#finds all doctors in entire city of SF that match that specialty, extracts
	#list of npi's
	if specialties:
		doctor_list = session.query(model.Provider).filter(model.Provider.specialty.in_(specialties))
		npi_list = [doctor.npi for doctor in doctor_list]

	# for dr in doctor_list:
	# 	print dr.specialty
	# finds all claims by all doctors in the list
	if doctor_list:
		npi_list = [doctor.npi for doctor in doctor_list]

	# this runs a separate query for each npi in the list - is there a better way?
	claims = session.query(model.Claim).filter(model.Claim.npi.in_(npi_list)).all()

	claim_prices = [claim.avg_submitted_chrg for claim in claims]
	return sum(claim_prices)/len(claim_prices)

@app.route('/provider')
def display_provider():
	npi = request.args.get("id")

	session = model.connect()

	provider = session.query(model.Provider).get(npi)

	return render_template('provider_page.html', provider = provider)

if __name__ == '__main__':
	app.run(debug=True)

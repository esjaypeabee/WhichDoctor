from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func
import model
import search
import numpy

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
	search_terms = request.args.get("specialty")

	session = model.connect()

	query = session.query(model.Provider)

	base_avg = None
	hcpcs_code = None

	# check if user entered anything
	if zipcode == '' and search_terms== '':
		return "Please enter a value"

	else:
		# if user entered only a zipcode
		if search_terms != '':
			search_terms = ''.join([c for c in search_terms if c not in PUNCTUATION])
			specialties = search.search_specialty(search_terms)
			query = query.filter(model.Provider.specialty.in_(specialties))
			base_avg = calc_base_avg(specialties = specialties)
			# base_avg = calc_base_avg(hcpcs_code = hcpcs_code)
			# query = query.join(model.Claim).filter(model.Claim.hcpcs_code == hcpcs_code)
			# hcpcs_code = int(hcpcs_code)
		else:
			specialties = None

		# if user entered only a diagnosis code 
		if zipcode != '':
			query = query.filter(model.Provider.short_zip == int(zipcode[:5]))

	# run the query
	doctor_list = query.limit(20).all()
	if doctor_list == []:
		return "No providers match your search! Try searching without a zip code."

	# check to see if base average has already been calculated, if not:
	# calculate the average based on all the claims from all the doctors.
	if base_avg == None:
		base_avg = calc_base_avg(doctor_list =doctor_list)

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
			dr.numdollars = "one"
		elif zscore <= -1:
			dr.dollars = "$$"
			dr.numdollars = "two"
		elif zscore < 1:
			dr.dollars = "$$$"
			dr.numdollars = "three"
		elif zscore < 2:
			dr.dollars = "$$$$"
			dr.numdollars = "four"
		else:
			dr.dollars = "$$$$$"
			dr.numdollars = "five"


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

	# KEEPING THIS FOR NOW BUT IS USELESS UNTIL TREATMENT SEARCH WORKS
	# finds all claims with a given treatment code
	# if expand beyond SF, change this to optionally limit by geographic area
	# if hcpcs_code:
	# 	claims = session.query(model.Claim).filter_by(hcpcs_code = hcpcs_code).all()	



@app.route('/provider')
def display_provider():
	npi = request.args.get("id")

	session = model.connect()

	provider = session.query(model.Provider).get(npi)

	return render_template('provider_page.html', provider = provider)

if __name__ == '__main__':
	app.run(debug=True)

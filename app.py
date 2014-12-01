from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func, distinct
import model
import search
import spellchecker
import ast
# import lookuptable

#### IT'S HCPCS

app = Flask(__name__)
app.secret_key = 'askjdfiwbueryqaowijfmcw037u41ojmpq9uqije12jnedmp2oq09ef0ccjwo'

PUNCTUATION = '!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'

@app.route("/")
def index():
	return render_template('index.html')

# def build_med_query(search_terms):


@app.route("/search_results")
def search_results():
	"""Displays a list of doctors matching a speciality in a zipcode (eventually)"""
	# change this later to be specialty. Get speciality as a dropdown menu??
	zipcode = request.args.get("zipcode")
	search_terms = request.args.get("search-terms")
	location_data = request.args.get("location-data")

	session = model.connect()

	query = session.query(model.Provider).distinct()

	# check if user entered anything
	if zipcode == '' and search_terms== '':
		return "Please enter a value"

	else:
		# if user entered a specialty
		if search_terms != '':
			
			specialties = search.specialty(search_terms)
			print "\n\n ************ found these specialties:  ", specialties,"\n\n"
			codes = search.procedure(search_terms)
			print "\n\n ************ found these codes: ",codes," \n\n"

			if codes == None and specialties == None:
				suggestions = spellchecker.generate_suggestions(search_terms)
				if suggestions == []:
					return "No providers match your search! Try a different term."
				else:
					return render_template('suggestions.html',zipcode=zipcode, suggestions=suggestions)

			else:
				if specialties:
					q1 = query.filter(model.Provider.specialty.in_(specialties))
					if not codes:
						print "\n\n ************ I'm using q1 \n\n"
						query = q1

				if codes:
					npis = session.query(model.Claim.npi).filter(model.Claim.hcpcs_code.in_(codes)).all()
		 			q2 = query.filter(model.Provider.npi.in_([npi[0] for npi in npis]))
		 			if not specialties:
		 				print "\n\n ************ I'm using q2 \n\n"
		 				query = q2
		 			else:
		 				print "\n\n ************ I'm using the union \n\n"
		 				query = q1.union(q2)

		if location_data and location_data != '':
			print "\n\n *************location data************ \n\n"
			print "Before:", type(location_data), location_data
			location_dict = ast.literal_eval(location_data)
			print "After:", type(location_dict), location_dict
			# ,model.Provider.lat > location_dict['minlat'], model.Provider.lng < location_dict['maxlng'], model.Provider.lng > location_dict['minlng']
			query = query.filter(model.Provider.lat < location_dict['maxlat'],model.Provider.lat > location_dict['minlat'], model.Provider.lng < location_dict['maxlng'], model.Provider.lng > location_dict['minlng'])
		# if user entered a zipcode 
		elif zipcode != '':
			query = query.filter(model.Provider.short_zip == int(zipcode[:5]))


	# run the query
	doctor_list = query.limit(20).all()

	if doctor_list == []:
		return "No providers match your search! Try searching without a zip code."

	for dr in doctor_list:
		if dr.zscore <= -1.5:
			dr.dollars = "$"
		elif dr.zscore <= -.5:
			dr.dollars = "$$"
		elif dr.zscore < .5:
			dr.dollars = "$$$"
		elif dr.zscore < 1.5:
			dr.dollars = "$$$$"
		else:
			dr.dollars = "$$$$$"


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

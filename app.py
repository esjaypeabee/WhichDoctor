from flask import Flask, render_template, redirect, request
from sqlalchemy import func, distinct
import model
import search
import spellchecker
import ast

#### Note to self:
#### IT'S HCPCS

app = Flask(__name__)
app.secret_key = 'askjdfiwbueryqaowijfmcw037u41ojmpq9uqije12jnedmp2oq09ef0ccjwo'

PUNCTUATION = '!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/search_results")
def search_results():
	"""
	Takes the user's search terms, zipcode, or a range of latitude/longitude 
	and returns a list of providers matching those search terms.
	"""

	# pull out parameters from the request
	zipcode = request.args.get("zipcode")
	search_terms = request.args.get("search-terms")
	location_data = request.args.get("location-data")

	# connect to database
	session = model.connect()

	# base query
	query = session.query(model.Provider).distinct()

	# check if user entered anything
	if not zipcode and not search_terms and not location_data:
		return "Please enter a value"

	# if the user entered something, build a query
	else:
		# if user entered something in the main search box
		if search_terms:
			
			# sends the search terms to search.py
			# search.py spilts the terms and checks them against PSQL indices
			# returns with a list of procedure code or a list of specialties 
			# that match the search terms
			specialties = search.specialty(search_terms)
			codes = search.procedure(search_terms)

			# if there are no matches
			if codes == None and specialties == None:
				# check spelling, and if nothing is mispelled direct user to 
				# enter a new term
				suggestions = spellchecker.generate_suggestions(search_terms)
				if suggestions == []:
					return "No providers match your search! Try a different term."
				else:
					return render_template('suggestions.html',zipcode=zipcode, 
								suggestions=suggestions)

			# if search.py finds matches
			else:
				if specialties:
					# filter for any applicable specialties
					q1 = query.filter(model.Provider.specialty.in_(specialties))
					if not codes:
						# if no procedures match, this becomes our base query
						query = q1

				if codes:
					# get a list of doctors that perform the procedures
					npis = session.query(model.Claim.npi)\
						.filter(model.Claim.hcpcs_code.in_(codes)).all()
		 			q2 = query.filter\
		 				(model.Provider.npi.in_([npi[0] for npi in npis]))
		 			if not specialties:
		 				query = q2
		 			else:
		 				# if the query matches both procedures and specialties,
		 				# use the union of those two queries
		 				query = q1.union(q2)

		# check if the user searched using the map
		if location_data:
			# change the location data to a python dictionary
			location_dict = ast.literal_eval(location_data)
			# filter providers using their latitude/longitude
			query = query.filter(model.Provider.lat < location_dict['maxlat'],\
				model.Provider.lat > location_dict['minlat'], \
				model.Provider.lng < location_dict['maxlng'], \
				model.Provider.lng > location_dict['minlng'])
		# otherwise, use any zipcode the user entered
		elif zipcode:
			query = query.filter(model.Provider.short_zip == int(zipcode[:5]))


	# run the query
	doctor_list = query.limit(20).all()

	if not doctor_list:
		return "No providers match your search! Try searching without a zip code."

	# assign the number of dollar signs to providers based on the number of 
	# standard deviations off the mean

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

@app.route('/provider')
def display_provider():
	"""Given a unique identifier for a doctor, display a page with the doctor's 
	contact information"""

	npi = request.args.get("id")

	session = model.connect()

	provider = session.query(model.Provider).get(npi)

	return render_template('provider_page.html', provider = provider)

if __name__ == '__main__':
	app.run(debug=True)

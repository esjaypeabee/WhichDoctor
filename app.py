from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func
import model
import numpy

#### IT'S HCPCS

app = Flask(__name__)
app.secret_key = 'askjdfiwbueryqaowijfmcw037u41ojmpq9uqije12jnedmp2oq09ef0ccjwo'


@app.route("/")
def index():
	return render_template('index.html')

@app.route("/search_results")
def search_results():
	"""Displays a list of doctors matching a speciality in a zipcode (eventually)"""
	# change this later to be specialty. Get speciality as a dropdown menu??
	zipcode = request.args.get("zipcode")
	hcpcs_code = request.args.get("hcpcs-code")

	session = model.connect()

	query = session.query(model.Provider)

	base_avg = None

	# check if user entered anything
	if zipcode == '' and hcpcs_code == '':
		return "Please enter a value"

	else:
		# if user entered only a zipcode
		if hcpcs_code != '':
			base_avg = calc_base_avg(hcpcs_code = hcpcs_code)
			query = query.join(model.Claim).filter(model.Claim.hcpcs_code == hcpcs_code)
			hcpcs_code = int(hcpcs_code)
		else:
			hcpcs_code = None

		# if user entered only a diagnosis code 
		if zipcode != '':
			query = query.filter(model.Provider.short_zip == int(zipcode[:5]))

	# run the query
	doctor_list = query.limit(20).all()

	# check to see if base average has already been calculated, if not:
	# calculate the average based on all the claims from all the doctors.
	if base_avg == None:
		base_avg = calc_base_avg(doctor_list =doctor_list)

	# calculate the average claim price for each doctor, optionally with code
	for doctor in doctor_list:
		dr_avg = doctor.priciness(hcpcs_code)
		doctor.rel_cost = ((dr_avg - base_avg)/base_avg)*100

	return render_template('search_results.html', doctor_list = doctor_list)

def calc_base_avg(hcpcs_code=None, doctor_list=None):
	"""With either a treatment code or a list of providers, caluculate the 
	average submitted charge across all claims of same type or all doctors in 
	the list."""

	session = model.connect()

	# returns a list of tuples - is there a better way?
	# finds all claims with a given treatment code
	# if expand beyond SF, change this to optionally limit by geographic area
	if hcpcs_code:
		claims = session.query(model.Claim).filter_by(hcpcs_code = hcpcs_code).all()

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

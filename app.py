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
	"""Displays a list of doctors matching a speciality in a zipcode"""
	# change this later to be specialty. Get speciality as a dropdown menu??
	zipcode = request.args.get("zipcode")
	hcpcs_code = request.args.get("hcpcs-code")

	session = model.connect()

	query = session.query(model.Provider)

	base_avg = None

	if zipcode == '' and hcpcs_code == '':
		return "Please enter a value"

	else:
		if hcpcs_code != '':
			base_avg = calc_base_avg(hcpcs_code = hcpcs_code)
			query = query.join(model.Claim).filter(model.Claim.hcpcs_code == hcpcs_code)
			hcpcs_code = int(hcpcs_code)
		else:
			hcpcs_code = None 
		if zipcode != '':
			query = query.filter(model.Provider.short_zip == int(zipcode[:5]))

	doctor_list = query.limit(20).all()
	print "I have a doctor list!"

	if base_avg == None:
		print "passing the doctor list to base avg"
		base_avg = calc_base_avg(doctor_list =doctor_list)
		print "got a base_avg = ", base_avg
	for doctor in doctor_list:
		print "I calculated each doctor's priciness."
		dr_avg = doctor.priciness(hcpcs_code)
		doctor.rel_cost = ((dr_avg - base_avg)/base_avg)*100

	return render_template('search_results.html', doctor_list = doctor_list)

def calc_base_avg(hcpcs_code=None, doctor_list=None):
	session = model.connect()

	# returns a list of tuples - is there a better way?
	if hcpcs_code:
		claim_prices_tup = session.query(model.Claim.avg_submitted_chrg).\
			filter_by(hcpcs_code = hcpcs_code).all()
	if doctor_list:
		print "I got a doctor_list in calc_base_avg"
		claim_prices_tup = []
		print "assigned claim_prices_tup"
		for doctor in doctor_list:
			claim_prices_tup[-1:] = session.query(model.Claim.avg_submitted_chrg).\
				filter_by(npi = doctor.npi).all()

	print "got a new claim_prices_tup = ", claim_prices_tup


	claim_prices = []
	for price in claim_prices_tup:
		claim_prices.append(price[0])

	return sum(claim_prices)/len(claim_prices)

if __name__ == '__main__':
	app.run(debug=True)

	#print "Average is", calc_base_avg(36415)

from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func
import model

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
	hspcs_code = request.args.get("hspcs-code")

	session = model.connect()

	query = session.query(model.Provider)

	if zipcode == '' and hspcs_code == '':
		return "Please enter a value"

	else:

		if hspcs_code != '':
			query = query.join(model.Claim).filter(model.Claim.hcpcs_code == hspcs_code)

		if zipcode != '':
			query = query.filter(model.Provider.short_zip == int(zipcode[:5]))
			print query

	doctor_list = query.limit(20).all()

	return render_template('search_results.html', doctor_list = doctor_list)

if __name__ == '__main__':
	app.run(debug=True)

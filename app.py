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
	"""Displays a list of doctors matching a speciality"""
	# change this later to be specialty. Get speciality as a dropdown menu??
	npi = request.args.get("npi")
	print npi
	doctor = model.session.query(model.Provider).get(npi)

	# later change this back to doctor_list and include a for loop in the
	# search results

	return render_template('search_results.html', doctor = doctor)

if __name__ == '__main__':
	app.run(debug=True)

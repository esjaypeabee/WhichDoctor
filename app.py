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
	zipcode = int(request.args.get("zipcode"))
	hspcscode = request.args.get("hspcs-code")

	# need to make this not break with multiple inputs
	# need to make a query that can handle filtering doctors by procedure and 
	# zip code and limit to 20.
	if not hspcscode:
		# print "no super dooper code"
		doctor_list = model.session.query(model.Provider).\
		filter_by(zipcode = zipcode).limit(20).all()
	elif not zipcode:
		# print "nowhere man"
		claim_list = model.session.query(model.Claim).\
		filter_by(hcpcs_code = hspcscode).limit(20).all()
		doctor_list = []
		for claim in claim_list:
			doctor_list.append(claim.provider)
	elif not zipcode and not hspcscode:
		return "Please enter a value"
	else:
		# print " I has both things!!!"
		claim_list = model.session.query(model.Claim).\
		filter_by(hcpcs_code = hspcscode).all()
		doctor_list = []
		for claim in claim_list:
			# print claim.provider.zipcode // 10000
			if claim.provider.zipcode // 10000 == zipcode:
				doctor_list.append(claim.provider)


		# doctor_list = model.session.query(model.Claim).join(model.Claim.provider).\
		# filter_by(hcpsc_code=hspcscode).all()
		# for doctor in doctor_list:
		# 	if doctor.zipcode > 99999: 
		# 		if doctor.zipcode // 10000 != zipcode:
		# 			doctor_list.remove(doctor)
		# 	else:
		# 		if doctor.zipcode != zipcode:
		# 			doctor_list.remove(doctor)


	print doctor_list

	return render_template('search_results.html', doctor_list = doctor_list)

if __name__ == '__main__':
	app.run(debug=True)

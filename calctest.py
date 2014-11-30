from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func, distinct, update
import model
import search
import numpy

session = model.connect()

def calc_specialties():
	specialty_dict = {}

	# get a list of specialties
	results = session.query(model.Provider.specialty).distinct().all()
	specialties = [result[0] for result in results]

	for specialty in specialties:

		#get all the doctors in that specialty
		doctors = session.query(model.Provider).distinct()\
			.filter(model.Provider.specialty == specialty).all()
		npis = [doctor.npi for doctor in doctors]

		claims = session.query(model.Claim).filter(model.Claim.npi.in_(npis))
		# print "\n\n ************ : ",specialty,": \n\n"
		# print "\n\n ************ submissions: \n\n", submissions, "\n\n"
		submissions = [claim.avg_submitted_chrg for claim in claims]

		submission_array = numpy.array(submissions)
		# stdev = numpy.std(submission_array)
		mean = numpy.mean(submission_array)
		stdev = numpy.std(submission_array)
		specialty_dict[specialty] = [mean, stdev]

	print specialty_dict


def calc_zscore():

	doctors = session.query(model.Provider).distinct().all()
	num_docs = len(doctors)
	counter = 0

	for doctor in doctors:
		doctor.find_avg()

		specialty = session.query(model.SpecialtyLookup)\
			.filter(model.SpecialtyLookup.specialty == doctor.specialty).first()
		mean = float(specialty.avg_claim)
		stdev = float(specialty.stdev)

		if stdev == 0:
			zscore = 0
		else:
			zscore = (doctor.avg - mean)/stdev

		doctor.zscore = zscore	
		# u = update(model.Provider).where(model.Provider.npi == doctor.npi)\
		# 	.values({'zscore': zscore})
		# session.execute(u)
		counter += 1
		session.add(doctor)

		print "\n\n ************* ", doctor.givenname ," ", doctor.surname,"'s zscore is now: ", zscore
		print counter, "/", num_docs, " \n\n"

	session.commit()



		# for dr in doctor_list:
		# 	zscore = (dr.avg - mean)/stdev
		# 	if zscore <= -2:
		# 		dr.dollars = "$"
		# 	elif zscore <= -1:
		# 		dr.dollars = "$$"
		# 	elif zscore < 1:
		# 		dr.dollars = "$$$"
		# 	elif zscore < 2:
		# 		dr.dollars = "$$$$"
		# 	else:
		# 		dr.dollars = "$$$$$"



		





def main():
	#calc_specialties()
	calc_zscore()

if __name__ == '__main__':
	main()
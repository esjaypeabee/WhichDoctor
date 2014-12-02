from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func, distinct, update
import model
import search
import numpy

session = model.connect()

def calc_specialties():
	"""
	Calculates the average claim and standard deviation within each specialty,
	and prints these values to a dictionary.
	"""
	specialty_dict = {}

	# get a list of specialties
	results = session.query(model.Provider.specialty).distinct().all()
	specialties = [result[0] for result in results]

	for specialty in specialties:

		#get all the doctors in that specialty
		doctors = session.query(model.Provider).distinct()\
			.filter(model.Provider.specialty == specialty).all()
		npis = [doctor.npi for doctor in doctors]

		# get all the claims filed by those doctors
		claims = session.query(model.Claim).filter(model.Claim.npi.in_(npis))
		submissions = [claim.avg_submitted_chrg for claim in claims]

		submission_array = numpy.array(submissions)
		mean = numpy.mean(submission_array)
		stdev = numpy.std(submission_array)
		specialty_dict[specialty] = [mean, stdev]

	print specialty_dict

def calc_zscore():
	"""
	Calculates the number of standard deviations away from the specialty mean 
	(zscore) each doctor's average claim amount is, and updates the database 
	with the doctor's zscore.
	"""
	# get all the doctors
	doctors = session.query(model.Provider).distinct().all()
	# count the number of doctors and set a counter to 0 for debugging purposes
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
		counter += 1
		session.add(doctor)

		print "\n\n", doctor.givenname ," ", doctor.surname,"'s zscore is now: ", zscore
		print counter, "/", num_docs, " \n\n"

	session.commit()


def main():
	calc_specialties()
	calc_zscore()

if __name__ == '__main__':
	# this is commented out so the database doesn't get reseeded.
	# main()
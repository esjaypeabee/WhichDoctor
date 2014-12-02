import model
import os
import csv
import time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import create_engine, or_, distinct, func 
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Text, Boolean
from pygeocoder import Geocoder
import spec_dict

SF_ZIPS = [94102, 94103, 94104, 94105, 
			94107, 94108, 94109, 94110, 
			94111, 94112, 94114, 94115, 
			94116, 94117, 94118, 94121, 
			94122, 94123, 94124, 94127, 
			94129, 94130, 94131, 94132, 
			94133, 94134, 94158]

# key for google geocoder
G_KEY = os.environ.get('G_KEY')

def load_providers(session, filename):
	"""
	Seeds the providers table with providers from medicare's tab separated file.

	Medicare's tab separated file contains every doctor that filed a claim in 
	2012. Each type of claim has one line, so any doctor can have multiple lines.
	The following checks are in place:
	- Checks whether the provider is in San Francisco using the provider's zip.
	- Checks whether the provider has already been added to session using the 
	provider_dict

	The database includes each provider's office's latitude and longitude. This
	is found using google's geocoder, which has a rate limit of 5 calls per 
	second. This loop has a time delay built in to avoid this rate limit.
	"""

	print "Loading providers..."

	provider_dict = {}

	with open(filename, 'rb') as csvfile:

		# skip the header line and copyright statement
		header = csvfile.next()
		copyright = csvfile.next()

		lines = csv.reader(csvfile, delimiter = '\t')

		for line in lines:
			# Check if provider is in SF
			if line[12] == 'US' and int(line[10].strip()[:5]) in SF_ZIPS:
				# check if provider is already in dictionary
				if provider_dict.get(line[0].strip()) == None:
					# if not, add to dictionary and add provider to session
					provider_dict[line[0].strip()] = 0
					provider = model.Provider()
					provider.npi 			  = line[0].strip()
					provider.surname 		  = line[1].strip() 
					provider.givenname 		  = line[2].strip() 
					provider.mi 			  = line[3].strip()
					provider.credential 	  = line[4].strip()
					provider.gender 		  = line[5].strip()
					provider.entity_type 	  = line[6].strip() 
					provider.addy1 			  = line[7].strip() 
					provider.addy2 			  = line[8].strip() 
					provider.city 			  = line[9].strip() 
					provider.zipcode 		  = line[10].strip()
					# the tab separate file only contains the provider's 9 digit
					# zip code, here it's loaded as the 5 digit code.
					provider.short_zip		  = provider.zipcode[:5]
					provider.state 			  = line[11].strip() 
					provider.country		  = line[12].strip()  
					provider.specialty 		  = line[13].strip() 
					provider.mc_participation = line[14].strip()

					full_address = provider.addy1 +' '+ provider.city +' '+ provider.state

					# feed the full address into the geocoder to get lat long
					geocode = Geocoder(G_KEY).geocode(full_address)
					provider.lat = geocode[0].coordinates[0]
					provider.lng = geocode[0].coordinates[1]

					session.add(provider)
					print "Adding to session: ", 
					    provider.npi, provider.givenname, provider.surname
					# delay the next call so that the google api doesn't kick 
					# the request out.
					time.sleep(1)

		session.commit()

def load_claims(session, filename):
	"""
	Seeds the claims table with data from medicare's tab separated file.
	"""

	with open(filename, 'rb') as csvfile:

		print "Loading Claims..."

		# skip the header line and copyright statement
		header = csvfile.next()
		copyright = csvfile.next()

		lines = csv.reader(csvfile, delimiter = '\t')

		for line in lines:
			if line[12].strip() == 'US':
				# check if a claim is in SF
				longzip = line[10].strip()
				short_zip = int(longzip[:5])

				if short_zip in SF_ZIPS:
					claim = model.Claim()
					claim.npi 				 = line[0].strip()
					claim.svc_place 		 = line[15].strip()
					claim.hcpcs_code 		 = line[16].strip()
					claim.line_svc_cnt 		 = line[18].strip()
					claim.bene_unique 		 = line[19].strip()
					claim.bene_day_svc_cnt 	 = line[20].strip()
					claim.avg_mc_allowed 	 = line[21].strip()
					claim.sd_mc_allowed 	 = line[22].strip()
					claim.avg_submitted_chrg = line[23].strip()
					claim.sd_submitted_chrg  = line[24].strip()
					claim.avg_mc_payment 	 = line[25].strip()
					claim.sd_mc_payment 	 = line[26].strip()
					session.add(claim)

		session.commit()

def load_procedures(session, filename):
	"""
	Seeds the procedures table with data from medicare's tab separated file.
	Since multiple doctors could file the same type of claim, each procedure
	could have multiple lines. This function checks if the procedure is already 
	in the table using a dictionary.
	"""

	with open(filename, 'rb') as csvfile:

		print "Loading Procedures..."

		procedure_dict = {}

		# skip the header line and copyright statement
		header = csvfile.next()
		copyright = csvfile.next()

		lines = csv.reader(csvfile, delimiter = '\t')

		for line in lines:
			if line[12].strip() == 'US':
				# check if procedure was claimed in SF
				longzip = line[10].strip()
				short_zip = int(longzip[:5])

				if short_zip in SF_ZIPS:
					procedure = model.Procedure()
					procedure.hcpcs_code 	= line[16].strip()
					procedure.hcpcs_descr 	= line[17].strip()
					procedure.hcpcs_tsv		= func.to_tsvector(procedure.hcpcs_descr)	
					if procedure_dict.get(procedure.hcpcs_code) == None:
						procedure_dict[procedure.hcpcs_code] = 0
						session.add(procedure)
						print "Adding to session: ", procedure.hcpcs_code, procedure.hcpcs_descr

		session.commit()

def load_specialty_lookup(session, filename):
	"""
	Seeds the table with provider specialties and their common english names, 
	as well as the average claim amounts using a separate csv and a python dictionary.
	"""

	with open(filename, 'rb') as csvfile:

		lines = csv.reader(csvfile, delimiter = ',')
		for line in lines:
			lookup = model.SpecialtyLookup()
			lookup.search_term = line[0].strip()
			lookup.search_tsv = func.to_tsvector(lookup.search_term)	
			lookup.specialty = line[1].strip()
			lookup.avg_claim = spec_dict.thedict[lookup.specialty][0]
			lookup.stdev = spec_dict.thedict[lookup.specialty][1]
			session.add(lookup)

	session.commit()

def main(session): 

	# due to dependencies between the tables, the databases must get seeded in 
	# this order. 
    load_providers(session, "Data/Medicare-Physician-and-Other-Supplier-PUF-CY2012/Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt")
    load_procedures(session, "Data/Medicare-Physician-and-Other-Supplier-PUF-CY2012/Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt")
    load_claims(session, "Data/Medicare-Physician-and-Other-Supplier-PUF-CY2012/Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt")
    # before running the last function, run the functions in calctest.py
    # load_specialty_lookup(session, "Data/specialtylookup.csv")


if __name__ == "__main__":
	pass
	# these are commented out so the database doesn't get reseeded.
    # s= model.connect()
    # main(s)


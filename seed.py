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

SF_ZIPS = [94102, 94103, 94104, 94105, 
			94107, 94108, 94109, 94110, 
			94111, 94112, 94114, 94115, 
			94116, 94117, 94118, 94121, 
			94122, 94123, 94124, 94127, 
			94129, 94130, 94131, 94132, 
			94133, 94134, 94158]

G_KEY = os.environ.get('G_KEY')


def load_providers(session, filename):
	print "Loading providers..."
	provider_dict = {}

	with open(filename, 'rb') as csvfile:

		# get rid of header line and copyright statement
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
					provider.short_zip		  = provider.zipcode[:5]
					provider.state 			  = line[11].strip() 
					provider.country		  = line[12].strip()  
					provider.specialty 		  = line[13].strip() 
					provider.mc_participation = line[14].strip()

					full_address = provider.addy1 +' '+ provider.city +' '+ provider.state
					print full_address
					# feed the full address into the geocoder to get lat long
					geocode = Geocoder(G_KEY).geocode(full_address)
					provider.lat = geocode[0].coordinates[0]
					provider.lng = geocode[0].coordinates[1]

					session.add(provider)
					print "Adding to session: ", provider.npi, provider.givenname, provider.surname
					# delay the next call so that the google api doesn't kick 
					# the request out.
					time.sleep(1)
					# print "adding provider to session"
		session.commit()

def load_claims(session, filename):

	with open(filename, 'rb') as csvfile:

		print "Loading Claims..."

		# get rid of header line and copyright statement
		header = csvfile.next()
		copyright = csvfile.next()

		lines = csv.reader(csvfile, delimiter = '\t')


		for line in lines:
			if line[12].strip() == 'US':
				#print "hi!"
				longzip = line[10].strip()
				short_zip = int(longzip[:5])
				#print "this claim is in SF!"
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

	with open(filename, 'rb') as csvfile:

		print "Loading Procedures..."

		procedure_dict = {}

		# get rid of header line and copyright statement
		header = csvfile.next()
		copyright = csvfile.next()

		lines = csv.reader(csvfile, delimiter = '\t')

		for line in lines:
			if line[12].strip() == 'US':
				#print "hi!"
				longzip = line[10].strip()
				short_zip = int(longzip[:5])
				#print "this claim is in SF!"
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

	with open(filename, 'rb') as csvfile:

		lines = csv.reader(csvfile, delimiter = ',')
		for line in lines:
			lookup = model.SpecialtyLookup()
			lookup.search_term = line[0].strip()
			lookup.search_tsv = func.to_tsvector(lookup.search_term)	
			lookup.specialty = line[1].strip()
			session.add(lookup)

	session.commit()

def main(session):
    # when running for real, remove echo = true
    load_providers(session, "Data/Medicare-Physician-and-Other-Supplier-PUF-CY2012/Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt")
    #load_procedures(session, "Data/Medicare-Physician-and-Other-Supplier-PUF-CY2012/Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt")
    load_claims(session, "Data/Medicare-Physician-and-Other-Supplier-PUF-CY2012/Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt")
    # load_specialty_lookup(session, "Data/specialtylookup.csv")
    # load_procedure_terms(session, "procedure_index.csv")
    # seed_claim_lookup(session, "procedure_index.csv")
    # add_specialty_terms(session, 'specialty_list.txt')



if __name__ == "__main__":
    s= model.connect()
    main(s)



# def add_specialty_terms(session, filename):
# 	f = open(filename)
# 	text = f.read()

# 	# # get rid of 2 header lines
# 	# headerline1 = f.next()
# 	# headerline2 = f.next()

# 	words = text.split()
# 	for word in words:
# 		lookup = model.Lookup()
# 		print "line is: ", text
# 		print "word is: ", word
# 		# line = lookup.specialty			
# 		# word = lookup.search_term
# 		# session.add(lookup)

# 	# session.commit()

# def load_procedure_terms(session, filename):

# 	with open(filename, 'rb') as csvfile:

# 		lines = csv.reader(csvfile, delimiter = ',')
# 		for line in lines:
# 			proc_term = model.ProcSearchTerm()
# 			proc_term.word = line[0]
# 			proc_term.frequency = len(line[1])
# 			session.add(proc_term)

# 	session.commit()


# def seed_claim_lookup(session, filename):

# 	#print "\n\n **************** Opening CSV ************ \n\n"
# 	with open(filename, 'rb') as csvfile:

# 		lines = csv.reader(csvfile, delimiter = ',')
# 		#print "\n\n **************** starting loop over the lines ************ \n\n"
# 		for line in lines:
# 			word = line[0]
# 			#print "\n\n **************** the word is: ", word, " ************ \n\n"
# 			if word != '':
# 				for code in lookuptable.procedure_dict[word]:
# 					#print "\n\n **************** the code ************", code, " \n\n"
# 					claim_lookup = model.ClaimLookup()
# 					claim_lookup.word_id = session.query(model.ProcSearchTerm.id).filter(model.ProcSearchTerm.word == word).one()[0]
# 					claim_lookup.hcpcs_code = str(code)
# 					session.add(claim_lookup)
#			session.commit()


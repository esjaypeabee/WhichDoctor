import model
import csv


SF_ZIPS = [94102, 94103, 94104, 94105, 
			94107, 94108, 94109, 94110, 
			94111, 94112, 94114, 94115, 
			94116, 94117, 94118, 94121, 
			94122, 94123, 94124, 94127, 
			94129, 94130, 94131, 94132, 
			94133, 94134, 94158]



def load_providers(session, filename):
	provider_dict = {}

	with open(filename, 'rb') as csvfile:

		# get rid of header line and copyright statement
		header = csvfile.next()
		copyright = csvfile.next()

		lines = csv.reader(csvfile, delimiter = '\t')

		for line in lines:
			# print "building a provider"
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
			if provider_dict.get(provider.npi) == None:
				print "check if in provider_dict"
				provider_dict[provider.npi] = 0
				if provider.country == 'US' and (int(provider.short_zip) in SF_ZIPS):
					session.add(provider)
					print "adding provider to session"
		session.commit()

def load_claims(session, filename):

	with open(filename, 'rb') as csvfile:

		# print "Load claims got called!"

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
					claim.hspcs_descr 		 = line[17].strip()
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



def main(session):
    # when running for real, remove echo = true
    # load_providers(session, "Data/Medicare-Physician-and-Other-Supplier-PUF-CY2012/Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt")
    load_claims(session, "Data/Medicare-Physician-and-Other-Supplier-PUF-CY2012/Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt")



if __name__ == "__main__":
    s= model.connect()
    main(s)

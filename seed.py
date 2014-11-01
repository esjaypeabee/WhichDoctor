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

	with open(filename, 'rb') as csvfile:

		# get rid of header line and copyright statement
		header = csvfile.next()
		copyright = csvfile.next()

		lines = csv.reader(csvfile, delimiter = '\t')

		for line in lines:
			provider = model.Provider()
			provider.npi = line[0].strip()
			provider.surname = line[1].strip() 
			provider.givenname = line[2].strip() 
			provider.mi = line[3].strip()
			provider.credential = line[4].strip()
			provider.gender = line[5].strip()
			provider.entity_type = line[6].strip() 
			provider.addy1 = line[7].strip() 
			provider.addy2 = line[8].strip() 
			provider.city = line[9].strip() 
			provider.zipcode = line[10].strip() 
			provider.state 	= line[11].strip() 
			provider.country = line[12].strip()  
			provider.specialty = line[13].strip() 
			provider.mc_participation = line[14].strip()

			Try
			short_zip = int(provider.zipcode) // 10000
			#print short_zip 
			if short_zip in SF_ZIPS:
				session.add(provider)

		session.commit()

def main(session):
    # when running for real, remove echo = true
    load_providers(session, "Data/Medicare-Physician-and-Other-Supplier-PUF-CY2012/Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt")


if __name__ == "__main__":
    s= model.connect()
    main(s)

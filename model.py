from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session


Base = declarative_base()

ENGINE = create_engine("sqlite:///medicare_claims.db", echo=True)
session = scoped_session(sessionmaker(bind = ENGINE,
                                        autocommit = False,
                                        autoflush = False))

class Provider(Base):
	"""All of the providers who submitted medicare claims in 2012"""
	__tablename__ = "providers"

	npi 				= Column(Integer, primary_key = True)
	surname		 		= Column(String(64), nullable = True) 
	givenname 			= Column(String(64), nullable = True) 
	mi 					= Column(String(64), nullable = True)
	credential			= Column(String(64), nullable = True)
	gender 				= Column(String(5), nullable = True)
	entity_type			= Column(String(5), nullable = True) 
	addy1 				= Column(String(64), nullable = True) 
	addy2 				= Column(String(64), nullable = True) 
	city 				= Column(String(64), nullable = True) 
	zipcode 			= Column(Integer, nullable = True)
	short_zip			= Column(Integer, nullable = True) 
	state 				= Column(String(5), nullable = True) 
	country 			= Column(String(5), nullable = True)  
	specialty 			= Column(String(64), nullable = True) 
	mc_participation 	= Column(String(5), nullable = True) 


class Claim(Base):
	"""Each row is a type of claim submitted in the calendar year 2012"""
	__tablename__ = "claims"

	id 					= Column(Integer, primary_key = True) 
	npi 				= Column(Integer, ForeignKey('providers.npi'),
							nullable = True)
	svc_place 			= Column(String(5), nullable = True)
	hcpcs_code 			= Column(Integer, nullable = True)
	hcpcs_descr 		= Column(String(64), nullable = True)
	# number of times this service was billed
	line_svc_cnt 		= Column(Integer, nullable = True)
	# number of unique patients who received this service 
	bene_unique 		= Column(Integer, nullable = True)
	# number of unique patients who recieved this service per day
	bene_day_svc_cnt 	= Column(Integer, nullable = True)
	avg_mc_allowed 		= Column(Float, nullable = True)
	sd_mc_allowed 		= Column(Float, nullable = True)
	avg_submitted_chrg 	= Column(Float, nullable = True)
	sd_submitted_chrg 	= Column(Float, nullable = True)
	avg_mc_payment 		= Column(Float, nullable = True)
	sd_mc_payment 		= Column(Float, nullable = True)

	provider = relationship("Provider", backref=backref("claims", order_by=id))


def connect():
    global ENGINE
    global Session

    ENGINE = create_engine("sqlite:///medicare_claims.db", echo=True)
    Session = sessionmaker(bind = ENGINE)

    return Session()

def main():
	pass
	# engine = create_engine("sqlite:///medicare_claims.db", echo=True)
	# Base.metadata.create_all(engine)

if __name__ == "__main__":
	main()
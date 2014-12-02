from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import create_engine, or_, distinct, func, select, cast 
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session


Base = declarative_base()
ENGINE = create_engine("postgresql+pg8000://postgres:1234@localhost/medicare_claims", echo=False)
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
	lat 				= Column(Float)
	lng 				= Column(Float) 
	zscore				= Column(Float)

	def find_avg(self):
		"""If a particular treatment is specified, takes the average
		submitted charge of this doctor for that treatment. If no treatment, 
		calculates the average of all of this doctor's claims."""

		charges = [float(claim.avg_submitted_chrg) for claim in self.claims]

		self.avg = (sum(charges))/len(charges)
		return self.avg



class Claim(Base):
	"""The claims each doctor submitted in 2012"""

	__tablename__ = "claims"

	id 				= Column(Integer, primary_key = True) 
	npi 			= Column(Integer, ForeignKey('providers.npi'),
							nullable = True)
	svc_place 		= Column(String(5), nullable = True)
	hcpcs_code 		= Column(String(16), ForeignKey('procedures.hcpcs_code'))
	# number of times this service was billed
	line_svc_cnt 	= Column(Float, nullable = True)
	# number of unique patients who received this service 
	bene_unique 	= Column(Float, nullable = True)
	# number of unique patients who recieved this service per day
	bene_day_svc_cnt = Column(Float, nullable = True)
	# average maximum amount medicare will pay for a procedure
	avg_mc_allowed 	= Column(Float, nullable = True)
	sd_mc_allowed 	= Column(Float, nullable = True)
	# average charge the provider submitted to medicare for a procedure
	avg_submitted_chrg = Column(Float, nullable = True)
	sd_submitted_chrg = Column(Float, nullable = True)
	# average amount medicare actually paid for a procedure
	avg_mc_payment 	= Column(Float, nullable = True)
	sd_mc_payment 	= Column(Float, nullable = True)

	provider = relationship("Provider", backref=backref("claims", order_by=id))
	procedure = relationship("Procedure", backref=backref("claims", order_by=id))

class Procedure(Base):
	"""The procedures doctors performed in 2012"""

	__tablename__ = 'procedures'

	hcpcs_code 		= Column(String(16), primary_key = True)
	hcpcs_descr 	= Column(String(64), nullable = True)
	hcpcs_tsv		= Column(TSVECTOR, index = True)

class SpecialtyLookup(Base):
	""" Doctor specialties, thier common english names, the average and 
	standard deviation for claim amounts in this specialty."""

	__tablename__ = 'lookup'

	id 			= Column(Integer, primary_key = True)
	search_term = Column(String(64))
	search_tsv 	= Column(TSVECTOR, index = True)
	specialty   = Column(Text)
	avg_claim 	= Column(Float)
	stdev		= Column(Float)

def connect():
    global ENGINE
    global Session

    ENGINE = create_engine("postgresql+pg8000://postgres:1234@localhost/medicare_claims", echo=True)
    Session = sessionmaker(bind = ENGINE)

    return Session()

def main():
	pass
	# engine = create_engine("sqlite:///medicare_claims.db", echo=True)
	# Base.metadata.create_all(engine)
	# Claim.__table__.create(bind = ENGINE)

if __name__ == "__main__":
	main()
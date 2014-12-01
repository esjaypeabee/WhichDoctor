from flask import Flask, render_template, redirect, request
from sqlalchemy import func, or_, create_engine, select, cast
import model
import re

ENGINE = create_engine("postgresql+pg8000://postgres:1234@localhost/medicare_claims", echo=False)

def is_toss_word(word):

	toss_words = ['doctor', 'room', 'care']
	if word in toss_words:
		return False
	else:
		return True

def split_terms(term):
	term_list = term.split()
	# dedupe words
	word_set = set(term_list)
	# check if word is important or not
	word_list = filter(is_toss_word, list(word_set))
	query_list = []

	for word in word_list:
		word = word.lower()
		# handle the dash issue with xrays
		if word == 'xray' or word == 'x-ray':
			word = 'xray | x-ray'
		query_list.append(word)

	return query_list


def specialty(term):
	conn = ENGINE.connect()

	# split up the search terms
	query_terms = split_terms(term)
	# base query
	query = select([model.SpecialtyLookup.specialty])\
		.where(model.SpecialtyLookup.search_tsv.match(query_terms[0],postgresql_reconfig='english'))
	# build more queries for intersection
	for term in query_terms[1:]:
		q = select([model.SpecialtyLookup.specialty])\
			.where(model.SpecialtyLookup.search_tsv.match(term,postgresql_reconfig='english'))
		query = query.intersect(q)

	# search for specialties in the lookup table
	specialty_list = conn.execute(query).fetchall()
	if specialty_list == []:
		#print "found nothing"
		return None
	else:
		#print "found these specialties:", specialty_list
		return [specialty[0] for specialty in specialty_list]

def procedure(term):
	conn = ENGINE.connect()

	# split up the search terms
	query_terms = split_terms(term)
	# base query
	query = select([model.Procedure.hcpcs_code])\
		.where(model.Procedure.hcpcs_tsv.match(query_terms[0],postgresql_reconfig='english'))
	# build more select objects for intersection
	for term in query_terms[1:]:
		q = select([model.Procedure.hcpcs_code])\
			.where(model.Procedure.hcpcs_tsv.match(term,postgresql_reconfig='english'))
		query = query.intersect(q)

	# run the query
	code_list = conn.execute(query).fetchall()
	if code_list == []:
		return None
	else:
		return [code[0] for code in code_list]
	

def main():
	pass
	#print procedure('hand xray')
	#print specialty('heart surgeon')

if __name__ == '__main__':
	main()

"""
THIS IS HOW WE QUERY NOW:

>>> select_thing = select([SpecialtyLookup.specialty]).where(SpecialtyLookup.search_tsv.match('urology',postgresql_reconfig='english'))
>>> conn = ENGINE.connect()
>>> result = conn.execute(select_thing).fetchall()

result is a list of tuples
or = |
and = & 
the whole query:  
specialties = conn.execute(select([SpecialtyLookup.specialty]).where(SpecialtyLookup.search_tsv.match('eye | brain',postgresql_reconfig='english'))).fetchall()

"""
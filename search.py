from flask import Flask, render_template, redirect, request
from sqlalchemy import func, or_, create_engine, select, cast
import model
import re

ENGINE = create_engine("postgresql+pg8000://postgres:1234@localhost/medicare_claims", echo=False)

def is_toss_word(word):
	"""
	Checks if a word in a user's search query is among a list of unimportant
	words.
	"""
	toss_words = ['doctor', 'room', 'care']
	if word in toss_words:
		return False
	else:
		return True

def split_terms(term):
	"""
	Takes a long string of search terms, splits the string into seperate terms
	and prepares them for querying.
	Note on x-rays: PSQL's text based search could not link xray and x-ray, so
	this function combines the two forms into one query.
	"""
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
	"""
	Takes search terms in a string, and queries a lookup table to retrieve 
	provider specialty.
	"""
	conn = ENGINE.connect()

	# split up the search terms
	query_terms = split_terms(term)
	# base query
	query = select([model.SpecialtyLookup.specialty])\
		.where(model.SpecialtyLookup.search_tsv\
		.match(query_terms[0],postgresql_reconfig='english'))
	# build more queries for intersection
	for term in query_terms[1:]:
		q = select([model.SpecialtyLookup.specialty])\
			.where(model.SpecialtyLookup.search_tsv\
			.match(term,postgresql_reconfig='english'))
		query = query.intersect(q)

	# search for specialties in the lookup table,
	# returns a list of tuples
	specialty_list = conn.execute(query).fetchall()
	if specialty_list == []:
		return None
	else:
		# remove specialties from their tuples
		return [specialty[0] for specialty in specialty_list]

def procedure(term):
	conn = ENGINE.connect()

	# split up the search terms
	query_terms = split_terms(term)
	# base query
	query = select([model.Procedure.hcpcs_code])\
		.where(model.Procedure.hcpcs_tsv\
		.match(query_terms[0],postgresql_reconfig='english'))
	# build more select objects for intersection
	for term in query_terms[1:]:
		q = select([model.Procedure.hcpcs_code])\
			.where(model.Procedure.hcpcs_tsv\
			.match(term,postgresql_reconfig='english'))
		query = query.intersect(q)

	# search for specialties in the lookup table,
	# returns a list of tuples
	code_list = conn.execute(query).fetchall()
	if code_list == []:
		return None
	else:
		# remove specialties from their tuples
		return [code[0] for code in code_list]	

def main():
	pass

if __name__ == '__main__':
	main()

"""
To take advantage of PSQL's full text search functionality, the app needs to 
change the search terms into a form called a 'TSQuery' and check it against a
pre-indexed column of 'TSVectors'. SQLAlchemy query objects will not do this, 
instead, a select object must be created and executed.

THIS IS HOW TO CREATE AND RUN A SELECT OBJECT:

>>> select_object = select([SpecialtyLookup.specialty])\
	.where(SpecialtyLookup.search_tsv\
	.match('urology',postgresql_reconfig='english'))
>>> conn = ENGINE.connect()
>>> result = conn.execute(select_object).fetchall()

result is a list of tuples
or = |
and = & 
the whole query:  
specialties = conn.execute(select([SpecialtyLookup.specialty])\
	.where(SpecialtyLookup.search_tsv\
	.match('eye | brain',postgresql_reconfig='english'))).fetchall()

"""
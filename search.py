from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func, or_
import model
import re

# words that are common and don't mean anything important
toss_words = ['doctor', 'room', 'care']

def search_specialty(term):
	session = model.connect()	

	# split up the search terms
	term_list = term.split()

	query_terms = []

	for word in term_list:
		word = word.lower()

		#check if word is important or not
		if word not in toss_words:
			# add it to list of query terms surrounded by percent signs
			query_terms.append(word + '%')

	#print query_terms

	# search for specialties in the lookup table
	specialty_list = session.query(model.Lookup).filter(*[model.Lookup.search_term.like(x) for x in query_terms]).all()
	# code for what happens if there is more than one match in the lookup table,
	# or if there are no matches, goes here.
	dr_list = session.query(model.Provider).filter(or_(*[model.Provider.specialty.like(lookup.specialty) for lookup in specialty_list])).all()

	# return dr_list
	# for dr in dr_list:
	# 	print dr.specialty
	return [lookup.specialty for lookup in specialty_list]

def main():
	
	search_specialty('primary heart')

if __name__ == '__main__':
	main()


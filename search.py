from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func
import model
import re

term_dict = {'bone': 'ortho',
			 'ear': 'oto',
			 'throat': 'laryn',
			 'skin': 'derm',
			 'heart': 'card',
			 'surgery': 'surg',
			 'surgeon': 'surg', 
			 'cancer': 'onco',
			 'blood': 'hema', 
			 'kidney': 'nephro',
			 'stomach': 'gastro',
			 'chiropractor': 'chiro'}
			 # maybe change these to regex to handle misspellings?

toss_words = ['doctor', 'room']

def search_specialty(term):
	session = model.connect()	

	term_list = term.split()
	query_words = ''

	for word in term_list:

		word = word.lower()

		if re.search('ist', word):
			loc = re.search('ist', word)
			word = word[:loc.start()]

		if word in toss_words:
			continue
		elif word in term_dict.keys():
			query_words = query_words + '%'+(term_dict[word])+'%'
		else:
			query_words = query_words + '%'+(word)+'%'

	print "\n\n ********************* query words ******************** \n\n"

	print query_words

	dr_list = session.query(model.Provider).filter(model.Provider.specialty.like(query_words)).all()

	print "\n\n ********************* Doctor List ******************** \n\n"

	print dr_list

	print "\n\n ***************************** List of Specialties ******************* \n\n"
	
	for dr in dr_list:
		print dr.specialty

def main():
	
	search_specialty("ear doctor")

if __name__ == '__main__':
	main()


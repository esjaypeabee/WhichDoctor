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
			 'kidney': 'nephro'}

def search_specialty(term):
	session = model.connect()	

	term_list = term.split()
	query_words = ''

	for word in term_list:

		if word in term_dict.keys():
			query_words = query_words + '%'+(term_dict[word])+'%'
		elif re.search('log', word):
			loc = re.search('log', word)
			word = word[:loc.start()]

			print "\n\n *************** new word ************** \n\n"
			print word

			query_words = query_words + '%'+(word)+'%'

		elif word.lower() == 'doctor':
			continue
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
	
	search_specialty("cancer doctor")

if __name__ == '__main__':
	main()


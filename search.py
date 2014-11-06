from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func
import model

term_dict = {'bone': 'ortho',
			 'ear': 'oto',
			 'throat': 'laryn',
			 'skin': 'derm',
			 'heart': 'card'}

def search_specialty(term):
	session = model.connect()	

	term_list = term.split()
	query_words = ''

	for word in term_list:

		if word in term_dict.keys():
			query_words = query_words + '%'+(term_dict[word])+'%'
		else:
			query_words = query_words + '%'+(word)+'%'

	print "**************************** \n\n"+ query_words +"\n\n ************************"

	dr_list = session.query(model.Provider).filter(model.Provider.specialty.like(query_words)).all()

	print "\n\n ********************* Doctor List ******************** \n\n"

	print dr_list

	"\n\n ***************************** List of Specialties ******************* \n\n"
	
	for dr in dr_list:
		print dr.specialty

def main():
	
	search_specialty("surgery")

if __name__ == '__main__':
	main()


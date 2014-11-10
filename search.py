from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func, or_
import model
import re

term_dict = {'bone': ['ortho'],
			 'ear': ['oto'],
			 'throat': ['laryn'],
			 'skin': ['derm'],
			 'heart': ['card'],
			 'surgery': ['surg'],
			 'surgeon': ['surg'],
			 'eye': ['opto', 'opht'],  #oph*t
			 'cancer': ['onco'],
			 'blood': ['hema'], 
			 'kidney': ['nephro'],
			 'stomach': ['gastro']}
			 # re.compile('chiro'): 'chiro'}
			 # maybe change these to regex to handle misspellings?
			 # ophthalmology

toss_words = ['doctor', 'room']

def search_specialty(term):
	session = model.connect()	

	term_list = term.split()


	for word in term_list:

		word = word.lower()

		if re.search('ist', word):
			loc = re.search('ist', word)
			word = word[:loc.start()]

		if word in toss_words:
			continue
		elif word in term_dict.keys():
			# print word
			# print term_dict[word]
			print "\n\n ********************* query words ******************** \n\n"
			for term in term_dict[word]:
				query_words = query_words + '%'+term+'%'
		#elif 
		else:
			query_words = query_words + '%'+(word)+'%'

	print "\n\n ********************* query words ******************** \n\n"

	print query_words
	#SELECT * FROM providers WHERE specialty LIKE "%opt%" OR specialty LIKE '%opht%';
	#dr_list = session.query(Provider).filter(or_ (Provider.specialty.like('%opt%'), Provider.specialty.like('%opht%'))).all()
	#dr_list = session.query(model.Provider).filter(model.Provider.specialty.like(query_words)).all()

	print "\n\n ********************* Doctor List ******************** \n\n"

	print dr_list

	print "\n\n ***************************** List of Specialties ******************* \n\n"
	
	for dr in dr_list:
		print dr.specialty

def main():
	
	search_specialty('eye doctor')
	# search_specialty("chiroalknvowia;")

if __name__ == '__main__':
	main()


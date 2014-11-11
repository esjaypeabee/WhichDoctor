from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func, or_
import model
import re

# term_dict = {'bone': ['ortho'],
# 			 'ear': ['oto'],
# 			 'throat': ['laryn'],
# 			 'skin': ['derm'],
# 			 'heart': ['card'],
# 			 'surgery': ['surg'],
# 			 'surgeon': ['surg'],
# 			 'eye': ['opto', 'opht'],  #oph?t
# 			 'cancer': ['onco'],
# 			 'blood': ['hema'], 
# 			 'kidney': ['nephro'],
# 			 'stomach': ['gastro']}
			 # re.compile('chiro'): 'chiro'}
			 # maybe change these to regex to handle misspellings?
			 # ophthalmology

toss_words = ['doctor', 'room']

def search_specialty(term):
	session = model.connect()	

	term_list = term.split()

	# Load in terms we know about here so we're not querying them multiple times.
	db_search_terms = session.query(model.Terms).all()
	db_search_terms = [{
		'term': re.compile(x.regex),
		'actual': ['%%%s%%' % (y) for y in x.actual_form.split(',')],
		'procedure': x.procedure}
		for x in db_search_terms
	]

	query_terms = []

	for word in term_list:
		word = word.lower()

		if re.search('ist', word):
			loc = re.search('ist', word)
			word = word[:loc.start()]

		if word in toss_words:
			continue

		matched = False
		for db_term in db_search_terms:
			if len(db_term['term'].findall(word)) > 0:
				query_terms = query_terms + db_term['actual']
				matched = True

		if not matched:
			query_terms.append('%'+(word)+'%')

	print "\n\n ********************* query words ******************** \n\n"

	print query_terms
	#SELECT * FROM providers WHERE specialty LIKE "%opt%" OR specialty LIKE '%opht%';
	#dr_list = session.query(Provider).filter(or_ (Provider.specialty.like('%opt%'), Provider.specialty.like('%opht%'))).all()
	dr_list = session.query(model.Provider).filter(or_(*[model.Provider.specialty.like(x) for x in query_terms])).all()

	print "\n\n ********************* Doctor List ******************** \n\n"

	print dr_list

	print "\n\n ***************************** List of Specialties ******************* \n\n"
	
	for dr in dr_list:
		print dr.specialty

def main():
	
	search_specialty('optometry')
	# search_specialty("chiroalknvowia;")

if __name__ == '__main__':
	main()


from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func, or_, distinct
import model
import re
import csv
import unicodedata

PUNCTUATION = '!"#$%&\'()*+,-./:;<=>?@[\]^_` {|}~'

def make_dict():
	session = model.connect()
	
	hcpcs_codes = session.query(distinct(model.Claim.hcpcs_code)).all()

	procedure_dict = {}

	for code in hcpcs_codes:
		# print "\n\n **************** code is :", code, "\n\n"
		# print "\n\n **************** code[0] is :", code[0], "\n\n"
		# print "\n\n **************** type of code[0] is :", type(code[0]), "\n\n"
		description = session.query(model.Claim.hcpcs_descr).filter_by(hcpcs_code=code[0]).first()[0]
		#print type(description)
		description = unicodedata.normalize('NFKD', description).encode('ascii','ignore')
		# print type(description), description
		words = description.split()
		# print "\n\n **************** words are :", words, "\n\n"

		words = filter(is_stop_word, words)
		# print words

		for word in words:
			#word = word.decode("latin-1")
			word = word.lower()

			word = ''.join([c for c in word if c not in PUNCTUATION])
			# print "\n\n **************** word is :", word, "\n\n"
			# print "\n\n **************** type of word is :", type(word), "\n\n"
			# print "\n\n **************** descr_index.get(word, []) is :", descr_index.get(word, []), "\n\n"
			result = procedure_dict.get(word, [])
			result.append(code[0])
			procedure_dict[word] = result
			# print "\n\n **************** descr_index[word] is now:", descr_index[word], "\n\n"

	print procedure_dict
	#return procedure_dict

def is_stop_word(word):
	stop_words = ['^of$', '[0-9]+', ' ','^exams?$'] 
	for term in stop_words:
		if re.match(term, word):
			return False
		else:
			return True

def write_to_csv(procedure_dict, filename):
	writer = csv.writer(open(filename, 'wb'))
	for key, value in procedure_dict.items():
   		writer.writerow([key, value])



def main():
	make_dict()
	#write_to_csv(procedure_dict, 'procedure_index.csv')

if __name__ == "__main__":
	main()




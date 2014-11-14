from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func, or_, distinct
import model
import re

PUNCTUATION = '!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'

def make_dict():
	session = model.connect()
	
	hcpcs_codes = session.query(distinct(model.Claim.hcpcs_code)).all()

	descr_index = {}

	for code in hcpcs_codes:
		# print "\n\n **************** code is :", code, "\n\n"
		# print "\n\n **************** code[0] is :", code[0], "\n\n"
		# print "\n\n **************** type of code[0] is :", type(code[0]), "\n\n"
		description = session.query(model.Claim.hcpcs_descr).filter_by(hcpcs_code=code[0]).first()[0]
		words = description.split()
		# print "\n\n **************** words are :", words, "\n\n"

		for word in words:
			word = ''.join([c for c in word if c not in PUNCTUATION])
			# print "\n\n **************** word is :", word, "\n\n"
			# print "\n\n **************** type of word is :", type(word), "\n\n"
			# print "\n\n **************** descr_index.get(word, []) is :", descr_index.get(word, []), "\n\n"
			result = descr_index.get(word, [])
			result.append(code[0])
			descr_index[word] = result
			# print "\n\n **************** descr_index[word] is now:", descr_index[word], "\n\n"

	print descr_index

def main():
	make_dict()

if __name__ == "__main__":
	main()




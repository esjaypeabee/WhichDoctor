import re, collections
import csv
import words

"""
Spellchecker based on Peter Norvig's algorithm. 

The steps involved in the algorithm are:
- Train a python dictionary (NWORDS) based on a large text (in this case, the 
  english dictionary and the procedure descriptions).
- Find all possible words within 2 edit distances of the misspelled word.
- Filter the edited words to find the ones that are in the python dictionary.
- Return the words that appear most frequently.

The original algorithm only returned one suggestion, I changed it to return all 
suggestions. This is frequently less than 5 words.

The first three functions below were responsible for training NWORDS. NWORDS was 
then saved in a separate file, so these functions only need to be run once.
"""
# def words(text): return re.findall('[a-z]+', text.lower()) 

# def train(features):
#     model = collections.defaultdict(lambda: 1)
#     for f in features:
#         model[f] += 1
#     return model

# NWORDS = train(words(file('en.dict').read()))

# def train_better(filename):
# 	with open(filename, 'rb') as csvfile:
# 		lines = csv.reader(csvfile, delimiter = ',')
# 		for line in lines:
# 			word = line[0]

# 			if NWORDS.get(word):
# 				NWORDS[word] += 1
#   print NWORDS

# set NWORDS equal to an external dictionary.
NWORDS = words.dictionary

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
  """
  Finds all words within one edit of a misspelled word. 

  An 'edit' is defined as:
  - deletion (removing a letter),
  - transposition (switching two letters), or
  - replacement (exchanging one letter for another)
  - insertion (adding a letter)
  """
  # finds all the splits of a given word for use in later edits.
  # the splits of 'it' are ('it', ''); ('i','t'); ( '','it');
  splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]

  # the following find all the words within one edit
  deletes    = [a + b[1:] for a, b in splits if b]
  transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
  replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
  inserts    = [a + c + b     for a, b in splits for c in alphabet]

  # returns a set to remove duplicates
  firstedits = set(deletes + transposes + replaces + inserts)
  return firstedits


def known_edits2(word):
  """
  Finds all words within two edits of the original misspelled word by calling 
  edits1 on the original word, getting a set of words, then calling edits1 on 
  that resultant set.
  """
  return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): 
  """
  Checks if a set of words is in the dictionary.
  """
  return set(w for w in words if w in NWORDS)

def correct(word):
  """
  Finds a list of suggestions by calling all the above functions
  """
  candidates = known([word]) or known(edits1(word)) or known_edits2(word)

  # for candidate in candidates:
  # 	print candidate, ", ", NWORDS['candidate']
  return candidates

def generate_suggestions(words):
  """
  Creates a list of words to send back to the app. This function will be
  called whenever a query in the app returns an empty list of specialties or 
  codes, so it first checks if the word is actually misspelled or just not
  in the database.
  """
  word_list = words.split()
  suggestions = []

  for word in word_list:
	 word.lower()
    # confirm the word is misspelled
	 if word not in NWORDS:
		  suggestions[-1:] = correct(word)
  return suggestions

def main():
	pass

if __name__ == "__main__":
	main()
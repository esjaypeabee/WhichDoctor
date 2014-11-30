import re, collections
import csv
import words

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
	#print NWORDS

NWORDS = words.dictionary

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   firstedits = set(deletes + transposes + replaces + inserts)
   #print firstedits
   return firstedits


def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def correct(word):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word)
    # print candidates
    for candidate in candidates:
    	print candidate, ", ", NWORDS['candidate']
    return candidates
    # return max(candidates, key=NWORDS.get)

def generate_suggestions(words):
	word_list = words.split()
	suggestions = []

	for word in word_list:
		word.lower()

		if word not in NWORDS:
			suggestions[-1:] = correct(word)
	return suggestions

def main():
	pass
	# train_better('procedure_index.csv')
	# suggestions = correct('hert')
	# print suggestions


if __name__ == "__main__":
	main()
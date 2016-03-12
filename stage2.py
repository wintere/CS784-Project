import csv
import datrie
import re
import string
import sys

brand_trie = datrie.Trie(string.printable)
correct_brand_name_candidates = 0
development_set_size = 0
fixc = 0

# Import the brand name dictionary into our trie object
with open('big_dict.csv', 'r') as brand_dict_csv_file:
	brand_dict_reader = csv.reader(brand_dict_csv_file, delimiter=',', quotechar='"')
	for brand in brand_dict_reader:
		b_name = brand[0]
		#add variations to dictionary
		for permutation in [b_name.upper(), b_name.title(), b_name.lower(), b_name]:
			brand_trie[permutation] = int(brand[1])

#print(brand_trie.keys())
# Now import all entries from the development set
with open('stage2_development_set.csv', 'r') as development_set_csv_file:
	development_set_reader = csv.reader(development_set_csv_file, delimiter=',', quotechar='"')
	# For each product, try to identify the brand name
	for product in development_set_reader:
		development_set_size += 1
		# First attempt: split the product name into an array of strings.
		product_name = product[0]
		substrings = product_name.split(' ')
		s_array = []
		for i in range(len(substrings) - 1):
			s_array.append(' '.join(substrings[i:]))
		print("Product: " + product[0])
		cands = []
		for substring in s_array:
			cand = brand_trie.prefixes(substring)
			if len(cand) > 0:
				cands.extend(cand)
		print("Candidates: ", cands)
		# if brand_trie.values(brand_nae_candidate.lower()):
		# 	print("Using candidate: \"" + brand_name_candidate + "\"")
		if product[1] in cands:
			# print("Correct brand is somewhere in candidates!")
			correct_brand_name_candidates += 1
		else:
			print("Correct brand not in candidates is (correct: " + product[1] + ")")
			fixc +=1
		# 	break
	print("\n\n")
	print("We aren't recognizing candidates in", fixc, "strings.")
		
# Output our results
# print("FINAL RESULTS:")
# print("Correctly identified " + str(correct_brand_name_candidates) + " brand names from a set of " + str(development_set_size) + " entries")
# print("Accuracy: " + str(correct_brand_name_candidates*100/development_set_size) + "%")
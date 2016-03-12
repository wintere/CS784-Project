import csv
import datrie
import re
import string
import sys

brand_trie = datrie.Trie(string.ascii_lowercase)
correct_brand_name_candidates = 0
development_set_size = 0

# Import the brand name dictionary into our trie object
with open('big_dict.csv', 'r') as brand_dict_csv_file:
	brand_dict_reader = csv.reader(brand_dict_csv_file, delimiter=',', quotechar='"')
	for brand in brand_dict_reader:
		brand_trie[brand[0].lower()] = int(brand[1])
		
# Now import all entries from the development set
with open('stage2_development_set.csv', 'r') as development_set_csv_file:
	development_set_reader = csv.reader(development_set_csv_file, delimiter=',', quotechar='"')
	# For each product, try to identify the brand name
	for product in development_set_reader:
		development_set_size += 1
		# First attempt: split the product name into an array of strings.
		product_name = re.split(r' ', product[0])
		print("Product: " + product[0])
		# Check the trie for each string, starting from the left. Assume the first matching string is the brand name.
		for brand_name_candidate in product_name:
			#print("Candidate: " + brand_name_candidate)
			#print(str(brand_trie.values(brand_name_candidate.lower())))
			if brand_trie.values(brand_name_candidate.lower()):
				print("Using candidate: \"" + brand_name_candidate + "\"")
				if brand_name_candidate.lower() == product[1].lower():
					print("Candidate is correct!")
					correct_brand_name_candidates += 1
				else:
					print("Candidate is incorrect (correct: " + product[1].lower() + ")")
				break
		print("\n\n")
		
# Output our results
print("FINAL RESULTS:")
print("Correctly identified " + str(correct_brand_name_candidates) + " brand names from a set of " + str(development_set_size) + " entries")
print("Accuracy: " + str(correct_brand_name_candidates*100/development_set_size) + "%")
import csv
import datrie
import re
import string
import sys
from collections import defaultdict

brand_trie = datrie.Trie(string.printable)
falsepositives = 0
falsenegatives = 0
truepositives = 0
truenegatives = 0
correct_guess_size = 0
development_set_size = 0
right = 0
syn_dict = dict()

# Import the brand name dictionary into our trie object
with open('big_dict.csv', 'r', encoding="latin-1") as brand_dict_csv_file:
    brand_dict_reader = csv.reader(brand_dict_csv_file, delimiter=',', quotechar='"')
    for brand in brand_dict_reader:
        b_name = brand[0]
        #add variations to dictionary
        #possibly remove
        smushed = ''.join(b_name.split(' '))
        permutations = [b_name.upper(), b_name.title(), b_name.lower(), smushed, smushed.lower(), smushed.title()]
        for permutation in permutations:
            brand_trie[permutation] = int(brand[1])
            syn_dict[permutation] = b_name

        brand_trie[b_name] = int(brand[1])

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
            #preprocess title?
            #tweak as necessary
            cand = brand_trie.prefixes(substring)
            final_cands = set()
            for c in cand:
                sub = False
                for st in substrings:
                    if (c in st) and (len(c) < len(st)):
                        sub = True
                if sub == False:
                    if c in syn_dict:
                        final_cands.add(syn_dict[c])
                    else:
                        final_cands.add(c)
            #print(cand)
            if len(cand) > 0:
                cands.extend(final_cands)
        print("Candidates: ", cands)
        # if brand_trie.values(brand_nae_candidate.lower()):
        # 	print("Using candidate: \"" + brand_name_candidate + "\"")

        # Heuristic that pulls out correct candidate
        chosen = ""
        candindex = defaultdict(list)
        lower_name = product_name.lower()
        for candidate in cands:
            index = lower_name.find(candidate.lower())
            candindex[index].append(candidate)
        if len(candindex) > 0:
            min_index = min(candindex)
            chosen = candindex[min_index][0]
            for candidate in candindex[min_index]:
                if len(candidate) > len(chosen):
                    chosen = candidate
        print("Chosen: ", chosen)
        
        if chosen == product[1]:
            correct_guess_size += 1
        else:
            print(product_name)
            print("Wrong Guess:", chosen, "Brand Name:", product[1])

        if (product[1] in cands):
            # print("Correct brand is somewhere in candidates!")
            truepositives += 1
            right += 1
        elif (product[1] == '' and cands == []):
            truenegatives += 1
            right += 1
        elif  (product[1] == '' and cands != []):
            print("False POS")
            falsepositives += 1
        elif (product[1] != '' and cands == []):
            print("False NEG: ", product[1], "correct")
            falsenegatives += 1
        else:
            print("guessed the wrong brand name")

# 	break
precision = correct_guess_size/float(development_set_size)
print("\n\n")
print("Correct Extraction:", correct_guess_size, "Precision:", precision)
print("True positives:", truepositives, "True negatives", truenegatives, "False positives", falsepositives, "False negatives", falsenegatives)
print("Overall ", right, "right")

# Output our results
# print("FINAL RESULTS:")
# print("Correctly identified " + str(correct_brand_name_candidates) + " brand names from a set of " + str(development_set_size) + " entries")
# print("Accuracy: " + str(correct_brand_name_candidates*100/development_set_size) + "%")
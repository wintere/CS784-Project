import csv
import datrie
import re
import string
import sys
from collections import defaultdict

if len(sys.argv) != 2:
    print("usage: pointer to csv of product name, brand name pairs")
    exit()

test_filepath = sys.argv[1]

# initialize tree that captures all characters and white spaces in its keys
brand_trie = datrie.Trie(string.printable)

true_positive = 0
true_negative = 0
false_positive = 0
false_negative = 0
product_count = 0

syn_dict = dict()

# Import the brand name dictionary into our trie object
with open('big_dict.csv', 'r', encoding="latin-1") as brand_dict_csv_file:
    brand_dict_reader = csv.reader(brand_dict_csv_file, delimiter=',', quotechar='"')
    for brand in brand_dict_reader:
        b_name = brand[0]
        b_name = b_name.title()
        # Add permutations of the brand name to our trie object.
        # These will help us catch things like different character casing, spacing, etc.
        smushed = ''.join(b_name.split(' '))
        dehyphen = ''.join(b_name.split('-'))
        permutations = [smushed.upper(),dehyphen.upper()]
        for permutation in permutations:
            brand_trie[permutation] = int(brand[1])
            #add a key, value pair that links transformed brand name to the original
            syn_dict[permutation] = b_name

        # Also record the frequency of each brand name to our trie
        brand_trie[b_name] = int(brand[1])

# Now import all entries from the development set
with open(test_filepath, 'r') as set_csv_file:
    set_reader = csv.reader(set_csv_file, delimiter=',', quotechar='"')
    
    # For each product, try to identify the brand name
    for product in set_reader:
        product_count += 1
        # Standardize product name (all caps)
        product_name = product[0].upper()
        # Replace () and | divider characters with spaces to split up brand names hidden in their substrings
        product_name = re.sub(r'\|\(\)',' ', product_name)
        substrings = product_name.split(' ')
        s_array = []
        # Because prefix only recognize substrings at the beginning of a string, divide string into substrings
        # to recognize brand names anywhere in the string
        for i in range(len(substrings) - 1):
            s_array.append(' '.join(substrings[i:]))

        # Identify which strings are candidates for brand name
        cands = []
        for substring in s_array:
            # Get candidates from prefix tree
            cand = brand_trie.prefixes(substring)
            final_cands = set()
            for c in cand:
                sub = False
                for st in substrings:
                    if (c in st) and (len(c) < len(st)):
                        sub = True
                    # Remove candidates that are less than 1 word (ie 'Sm' for 'Smart Technologies'
                    if (c == st):
                        break
                if sub == False:
                    # Return regularized versions of 'synonyms', ie. Cooler Master for Cooler Master
                    if c in syn_dict:
                        final_cands.add(syn_dict[c])
                    else:
                        final_cands.add(c)
            if len(cand) > 0:
                #Add acceptable candidates to final list
                cands.extend(final_cands)
        
        # Select the longest candidate at the earliest index of all candidates
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

        #retrieve label from golden data to check against computed brand name
        label = product[1].title()

        # If algorithm found a brand name, determine if true or false positive
        if chosen != '':
            if chosen == label:
                true_positive += 1
            elif label != '':
                false_positive += 1
                print("MISMATCH\nName:",product_name,"\nDetected:",chosen,"\nCorrect:",label)
            else:
                false_positive += 1
                print("FALSE POSITIVE\nName:", product_name,"\nDetected:",chosen)
        # If algorithm did not find l a brand name, determine if true or false negative
        else:
            if label == "":
                true_negative += 1
            else:
                false_negative += 1
                print("FALSE NEGATIVE\nName:",product_name,"\nCorrect:",label)

# All done! Output the results
print("Finished checking",str(product_count),"products...")
print("True Pos",true_positive, "False Pos",false_positive, "True Neg",true_negative, "False Neg", false_negative)
precision = float (true_positive)/(true_positive + false_positive)
recall = float(true_positive)/(true_positive + false_negative)
print ("Precision:",precision, "Recall:",recall)


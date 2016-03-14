import csv
import datrie
import re
import string
import sys
from collections import defaultdict

brand_trie = datrie.Trie(string.printable)
true_positive = 0
true_negative = 0
false_positive = 0
false_negative = 0
syn_dict = dict()
product_count = 0

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
        permutations = [smushed.upper(), b_name.upper(), dehyphen.upper()]
        for permutation in permutations:
            brand_trie[permutation] = int(brand[1])
            syn_dict[permutation] = b_name

        # Also record the frequency of each brand name to our trie
        brand_trie[b_name] = int(brand[1])

# Now import all entries from the development set
with open('stage2_development_set.csv', 'r') as development_set_csv_file:
    development_set_reader = csv.reader(development_set_csv_file, delimiter=',', quotechar='"')
    
    # For each product, try to identify the brand name
    for product in development_set_reader:
        
        product_count += 1
        
        # First attempt: split the product name into an array of strings.
        product_name = product[0].upper()
        product_name = re.sub(r'\|\(\)',' ', product_name)
        substrings = product_name.split(' ')
        s_array = []
        for i in range(len(substrings) - 1):
            s_array.append(' '.join(substrings[i:]))
        #print("Product: " + product[0])
        cands = []
        
        # Identify which strings are candidates for the real brand name
        for substring in s_array:
            # Preprocess title?
            cand = brand_trie.prefixes(substring)
            final_cands = set()
            for c in cand:
                sub = False
                for st in substrings:
                    if (c in st) and (len(c) < len(st)):
                        sub = True
                    if (c == st):
                        break
                if sub == False:
                    if c in syn_dict:
                        final_cands.add(syn_dict[c])
                    else:
                        final_cands.add(c)
            if len(cand) > 0:
                cands.extend(final_cands)
        #print("Candidates: ", cands)
        
        # The following heuristic determines the correct candidate
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
        #print("Chosen: ", chosen)

        label = product[1].title()
        
        # If this product name revealed a brand name, determine if true or false positive
        if chosen != '':
            if chosen == label:
                true_positive += 1
            elif label != '':
                false_positive += 1
            else:
                false_positive += 1
        # If this product name did not reveal a brand name, determine if true or false negative
        else:
            if label == "":
                true_negative += 1
            else:
                print("FALSE NEG")
                false_negative += 1

# All done! Output the results
print("Finished checking",str(product_count),"products...")
print("True Pos",true_positive, "False Pos",false_positive, "True Neg",true_negative, "False Neg", false_negative)
precision = float (true_positive)/(true_positive + false_positive)
recall = float(true_positive)/(true_positive + false_negative)
print ("Precision:",precision, "Recall:",recall)


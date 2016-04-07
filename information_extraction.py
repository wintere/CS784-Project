__author__ = 'wintere'

import csv
import datrie
import re
import string
import sys
from collections import defaultdict

class InformationExtractor:

    def __init__(self):

        #initialize brand trie
        brand_trie = datrie.Trie(string.printable)
        syn_dict = dict()
        with open('big_dict.csv', 'r') as brand_dict_csv_file:
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
        self.brand_trie = brand_trie
        self.syn_dict = syn_dict

        #color dict
        self.colors = []
        with open('colors.txt','r') as c_file:
            for c in c_file.readlines():
                self.colors.append(c.strip('\n'))


    def color_from_name(self, product_name):
        colors = []
        product_name = product_name.lower()
        product_name_list = product_name.split()
        for i in product_name_list:
            if i in self.colors:
                if i not in colors:
                    colors.append(i)
        return colors

    def brand_from_string(self, product_name):
        product_name = product_name.upper()
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
            cand = self.brand_trie.prefixes(substring)
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
                    if c in self.syn_dict:
                        final_cands.add(self.syn_dict[c])
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

        return chosen
__author__ = 'wintere'

import csv
import lxml
import datrie
import re
import string
import sys
from collections import defaultdict
from bs4 import BeautifulSoup
import pickle

class InformationExtractor:

    def __init__(self):

        #initialize brand trie
        brand_trie = datrie.Trie(string.printable)
        syn_dict = dict()
        with open('big_dict.csv', 'r', encoding='latin-1') as brand_dict_csv_file:
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
        self.longd_tfidf = pickle.load(open("tfidf_longd.p", "rb"))
        self.pname_tfidf = pickle.load(open("tfidf_pname.p", "rb"))

    def text_from_html(self, description):
        if len(description) < 5:
            return description.lower()
        try:
            html = BeautifulSoup(description, "lxml")
            # html = BeautifulSoup(description)
            text = html.getText(' ')
            if text is None:
                return description.lower()
            else:
                text = re.sub(r'[^\x00-\x7F]+',' ', text)
                return text.lower()
        except UserWarning:
            return description.lower()

    # a cheap haaaack
    def brand_adjuster(self, d, ld=False):
        if ld:
            for entry in ['brand', 'product name', 'manufacturer', 'product short description', 'product long description', 'brand name']:
                if entry in d:
                    cur = d.get(entry).lower()
                    cur = cur.replace('cables to go', 'c2g')
                    cur = cur.replace('startech.com', 'startech')
                    cur = cur.replace('pny technologies', 'pny')
                    cur = cur.replace('everki usa inc', 'everki')
                    cur = cur.replace('rubbermaid home', 'rubbermaid')
                    d[entry] = cur
        else:
            for entry in ['brand', 'product name', 'manufacturer', 'product short description', 'product long description', 'brand name']:
                if entry in d:
                    cur = d.get(entry)[0].lower()
                    cur = cur.replace('cables to go', 'c2g')
                    cur = cur.replace('startech.com', 'startech')
                    cur = cur.replace('pny technologies', 'pny')
                    cur = cur.replace('everki usa inc', 'everki')
                    cur = cur.replace('rubbermaid home', 'rubbermaid')
                    d[entry] = [cur]
        return d

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

        return chosen.lower()

    #moved from feature_operations for better modularity
    def unitsFromString(self, tokens):
        measurement_units = ['khz', 'mhz', 'ghz', 'watt', 'nm', 'um', 'mm', 'cm', 'm', 'km', 'ft', 'in', 's', 'ms', 'mb', 'gb', 'tb', 'gb/s', 'mb/s', 'mbps', 'awg', 'a', 'w', 'g', 'lb', 'dba', 'cfm', 'rpm', 'amp', 'mah', 'watts', 'vac']
        units = []
        for index in range(0, len(tokens)):
            token = tokens[index].lower()
            # Look for units split across multiple tokens
            if re.match("^[0-9\.]+$", token):
                if index < len(tokens) - 1:
                    nextToken = str(tokens[index + 1]).lower().replace(".", "")
                    if nextToken in measurement_units:
                        unit_value = re.sub(r'\.[0]+', "", token)  # Remove any trailing decimal points + 0s
                        # print("Token=" + str(token) + ", unit value=" + str(unit_value))
                        units.append(str(unit_value + " " + nextToken))
            # Also look for units compacted into a single token
            elif re.match("^[0-9\.]+(\s)*[a-z\./]+$", token):
                unit_data = re.match("^([0-9\.]+)[\s]*([a-z\./]+)$", token)
                if str(unit_data.groups(0)[1]) in measurement_units:
                    unit_value = re.sub(r'\.[0]+', "",
                                               unit_data.groups(0)[0])  # Remove any trailing decimal points + 0s
                    # print("Token=" + str(token) + ", unit value=" + str(unit_value))
                    units.append(str(unit_value) + " " + str(unit_data.groups(0)[1]))
        return units

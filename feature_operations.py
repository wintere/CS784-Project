__author__ = 'wintere'

import py_stringmatching.tokenizers
import py_stringmatching.simfunctions
from information_extraction import InformationExtractor
from html_parser import MyHtmlParser

#Rules to nest in:
#always return MISMATCH or FALSE if 'stress testing DO NOT BUY' in product name
#as these are not real products

pld = 'Product Long Description'

#helper method
def fetchSet(dict, key):
    if key not in dict:
        return []
    val = dict[key]
    if isinstance(val, str):
        return [val]
    else:
        return val

class FeatureGenerator:
    def __init__(self):
        self.ie = InformationExtractor()
        self.parser = MyHtmlParser()
        self.syn_dict = self.ie.syn_dict

    #CHECKED
    def product_name_jaccard(self, l, r):
        p1 = l.get('Product Name')[0].lower()
        p2 = r.get('Product Name')[0].lower()
        p1_tokens = py_stringmatching.tokenizers.whitespace(p1)
        p2_tokens = py_stringmatching.tokenizers.whitespace(p2)
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #CHECKED
    def product_name_tfidf(self,l, r):
        p1 = l.get('Product Name')[0].lower()
        p2 = r.get('Product Name')[0].lower()
        p1_tokens = py_stringmatching.tokenizers.whitespace(p1)
        p2_tokens = py_stringmatching.tokenizers.whitespace(p2)
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)


    def is_stress_test(self, l, r):
        p1 = l.get('Product Name')
        p2 = r.get('Proudct Name')
        if (p1 is not None and 'stress testing' in p1[0].lower()) or (p2 is not None and 'stress testing' in p2[0].lower()):
            return 1
        else:
            return 0

    #CHECKED
    def product_short_description_tfidf(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Short Description')
        p2 = r.get('Product Short Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)

    #CHECKED
    def product_short_description_jaccard(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Short Description')
        p2 = r.get('Product Short Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #CHECKED
    def total_key_similarity(self, l, r, lld, rld):
        l_keys = list(l.keys())
        r_keys = list(r.keys())
        lld_keys = list(lld.keys())
        rld_keys = list(rld.keys())
        l_keys.extend(lld_keys)
        r_keys.extend(rld_keys)
        l_keys = [x.lower() for x in l_keys]
        r_keys = [x.lower() for x in r_keys]
        return py_stringmatching.simfunctions.jaccard(l_keys, r_keys)


    #CHECKED
    def long_descript_key_sim(self, l, r, lld, rld):
        lld_keys = list(lld.keys())
        rld_keys = list(rld.keys())
        lld_keys = [x.lower() for x in lld_keys]
        rld_keys = [x.lower() for x in rld_keys]
        return py_stringmatching.simfunctions.jaccard(lld_keys, rld_keys)

    #CHECKED
    def product_long_description_tfidf(self,l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Long Description')
        p2 = r.get('Product Long Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)

    #CHECKED
    def product_long_description_jaccard(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Long Description')
        p2 = r.get('Product Long Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #CHECKED
    def product_type_sim(self,l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1_tokens.extend(fetchSet(l,'Product Type'))
        p1_tokens.extend(fetchSet(lld, 'Product Type'))
        p2_tokens.extend(fetchSet(r,'Product Type'))
        p2_tokens.extend(fetchSet(rld, 'Product Type'))
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #CHECKED
    def product_segment_jaccard(self,l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Segment')
        p2 = r.get('Product Segment')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #CHECKED
    def manufacturer_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Manufacturer')
        p2 = r.get('Manufacturer')
        
        # If these fields don't exist in the main key-value set, then check the parsed Product Long Description data.
        if p1 is None and 'Manufacturer' in lld.keys():
            p1 = [lld.get('Manufacturer')]
        if p2 is None and 'Manufacturer' in rld.keys():
            p2 = [rld.get('Manufacturer')]
        
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #STRING DISTANCE INSTEAD?
    def manufacturer_part_number_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Manufacturer Part Number')
        p2 = r.get('Manufacturer Part Number')
 
        # If these fields don't exist in the main key-value set, then check the parsed Product Long Description data.
        if p1 is None and 'Manufacturer Part Number' in lld.keys():
            p1 = [lld.get('Manufacturer Part Number')]
        if p2 is None and 'Manufacturer Part Number' in rld.keys():
            p2 = [rld.get('Manufacturer Part Number')]

        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #CHECKED
    def assembled_product_length_sim(self, l, r, lld, rld):
        p1 = ''
        p2 = ''
        if 'Assembled Product Length' in l:
            p1 = l.get('Assembled Product Length')[0]
        if 'Assembled Product Length' in r:
            p2 = r.get('Assembled Product Length')[0]
        if p1 is '' and 'Assembled Product Length' in lld:
            p1 = lld.get('Assembled Product Length')
        if p2 is '' and 'Assembled Product Length' in rld:
            p2 = rld.get('Assembled Product Length')
        y = max(len(p1), len(p2))
        if y > 0:
            return py_stringmatching.simfunctions.levenshtein(p1, p2)/y
        return 1

    #CHECKED
    def assembled_product_width_sim(self, l, r, lld, rld):
        p1 = ''
        p2 = ''
        if 'Assembled Product Width' in l:
            p1 = l.get('Assembled Product Width')[0]
        if 'Assembled Product Width' in r:
            p2 = r.get('Assembled Product Width')[0]
        if p1 is '' and 'Assembled Product Width' in lld:
            p1 = lld.get('Assembled Product Width')
        if p2 is '' and 'Assembled Product Width' in rld:
            p2 = rld.get('Assembled Product Width')
        y = max(len(p1), len(p2))
        if y > 0:
            return py_stringmatching.simfunctions.levenshtein(p1, p2)/y
        return 1

    #CHECKED
    def color_match(self, l, r, lld, rld):
        l_color = set()
        r_color = set()
        # step 1: try it the easy way
        if 'Color' in l:
            l_color.add(l['Color'][0])
        elif 'Actual Color' in l:
            l_color.add(l['Actual Color'][0])
        if 'Color' in r:
            r_color.add(r['Color'][0])
        elif 'Actual Color' in r:
            r_color.add(r['Actual Color'][0])
        # add colors in product name
        l_name = l.get('Product Name')[0]
        l_color = l_color.union(self.ie.color_from_name(l_name))
        r_name = r.get('Product Name')[0]
        r_color = r_color.union((self.ie.color_from_name(r_name)))

        if 'Color' in lld:
            l_color = l_color.union(fetchSet(lld, 'Color'))
        if 'Color' in rld:
            r_color = r_color.union(fetchSet(rld, 'Color'))
        l_color = [x.lower() for x in l_color]
        r_color = [x.lower() for x in r_color]
        return py_stringmatching.simfunctions.jaccard(l_color, r_color)


    #CHECKED
    def big_text_jaccard(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1_keys = l.keys()
        p2_keys = r.keys()
        for key in p1_keys:
            p1_tokens.extend(py_stringmatching.tokenizers.whitespace(key))
            p1_tokens.extend(py_stringmatching.tokenizers.whitespace(l.get(key)[0]))
        for key in p2_keys:
            p2_tokens.extend(py_stringmatching.tokenizers.whitespace(key))
            p2_tokens.extend(py_stringmatching.tokenizers.whitespace(r.get(key)[0]))
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)


    #CHECKED
    def big_text_tfidf(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1_keys = l.keys()
        p2_keys = r.keys()
        for key in p1_keys:
            p1_tokens.extend(py_stringmatching.tokenizers.whitespace(key))
            p1_tokens.extend(py_stringmatching.tokenizers.whitespace(l.get(key)[0]))
        for key in p2_keys:
            p2_tokens.extend(py_stringmatching.tokenizers.whitespace(key))
            p2_tokens.extend(py_stringmatching.tokenizers.whitespace(r.get(key)[0]))
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)

    #CHECKED
    def brand_and_brand_name_sim(self, l, r, lld, rld):
        p1 = l.get('Brand')
        p2 = r.get('Brand')
        if p1 is None and 'Brand Name' in l.keys():
            p1 = l.get('Brand Name')
        if p2 is None and 'Brand Name' in r.keys():
            p2 = r.get('Brand Name')
        if p1 is None and 'Brand' in lld.keys():
            p1 = lld.get('Brand')
        if p2 is None and 'Brand' in rld.keys():
            p2 = rld.get('Brand')
        if p1 is None and 'Brand Name' in lld.keys():
            p1 = lld.get('Brand Name')
        if p2 is None and 'Brand Name' in rld.keys():
            p2 = rld.get('Brand Name')
        if p1 is None and p2 is None:
            return 0.0
        if p1 is None:
            p1 = [""]
        if p2 is None:
            p2 = [""]
        return py_stringmatching.simfunctions.jaro(p1[0].lower(), p2[0].lower())


    def getVector(self, l, r):
        #initialize vector and empty lld and rld (left long descript, right long descript)
        rld = {}
        lld = {}
        vector = []

        #parse html in long descriptions, if any
        if pld in l.keys():
            self.parser.reset()
            self.parser.result = {}
            self.parser.feed(l[pld][0])
            lld = self.parser.result
        if pld in r.keys():
            self.parser.reset()
            self.parser.result = {}
            self.parser.feed(r[pld][0])
            rld = self.parser.result


        # functions that do not take in long description dictionaries
        for func in self.is_stress_test, self.product_long_description_tfidf, self.big_text_tfidf, self.product_name_tfidf, self.big_text_jaccard, self.product_segment_jaccard:
            x = func(l, r)
            vector.append(x)

        # functions that do
        for func in self.long_descript_key_sim, self.total_key_similarity, self.color_match, self.manufacturer_jaccard, self.brand_and_brand_name_sim, self.color_match, self.product_type_sim, self.manufacturer_part_number_jaccard,self.assembled_product_width_sim, self.assembled_product_length_sim, self.long_descript_key_sim:
            y = func(l, r, lld, rld)
            vector.append(y)

        return vector
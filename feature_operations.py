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
    else:
        return dict[key]

class FeatureGenerator:
    def __init__(self):
        self.ie = InformationExtractor()
        self.parser = MyHtmlParser()
        self.syn_dict = self.ie.syn_dict

    def product_name_jaccard(self, l, r):
        p1 = l.get('Product Name')[0]
        p2 = r.get('Product Name')[0]
        p1_tokens = py_stringmatching.tokenizers.whitespace(p1)
        p2_tokens = py_stringmatching.tokenizers.whitespace(p2)
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def product_name_tfidf(self,l, r):
        p1 = l.get('Product Name')[0]
        p2 = r.get('Product Name')[0]
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

    def product_short_description_tfidf(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Short Description')
        p2 = r.get('Product Short Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)
        
    def product_short_description_jaccard(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Short Description')
        p2 = r.get('Product Short Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def total_key_similarity(self, l, r, lld, rld):
        l_keys = list(l.keys())
        r_keys = list(r.keys())
        lld_keys = list(lld.keys())
        rld_keys = list(rld.keys())
        l_keys.extend(lld_keys)
        r_keys.extend(rld_keys)
        return py_stringmatching.simfunctions.monge_elkan(l_keys, r_keys)


    def long_descript_key_sim(self, l, r, lld, rld):
        lld_keys = list(lld.keys())
        rld_keys = list(rld.keys())
        if len(lld_keys) == 0 or len(rld_keys) == 0:
            return 0
        else:
            return py_stringmatching.simfunctions.monge_elkan(lld_keys, rld_keys)

    def product_long_description_tfidf(self,l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Long Description')
        p2 = r.get('Product Long Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)
        
    def product_long_description_jaccard(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Long Description')
        p2 = r.get('Product Long Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def product_type_tfidf(self,l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Type')
        p2 = r.get('Product Type')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)
        
    def product_type_jaccard(self,l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Type')
        p2 = r.get('Product Type')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def product_segment_tfidf(self,l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Segment')
        p2 = r.get('Product Segment')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)
        
    def product_segment_jaccard(self,l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Product Segment')
        p2 = r.get('Product Segment')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)
        
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
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)
        
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
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)
        
    def assembled_product_length_jaccard(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Assembled Product Length')
        p2 = r.get('Assembled Product Length')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)
        
    def assembled_product_width_jaccard(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('Assembled Product Width')
        p2 = r.get('Assembled Product Width')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def brand_name_sim(self,l, r):
        p1 = l.get('Brand')
        p2 = r.get('Brand')
        if p1 is None:
            p1 = self.ie.brand_from_string(l.get('Product Name')[0])
        else:
            p1 = p1[0]
            if p1 in self.syn_dict:
                p1 = self.syn_dict[p1]
        if p2 is None:
            p2 = self.ie.brand_from_string(r.get('Product Name')[0])
        else:
            p2 = p2[0]
            if p2 in self.syn_dict:
                p2 = self.syn_dict[p2]
        return py_stringmatching.simfunctions.jaro_winkler(p1, p2)

    def category_match(self, l, r):
        l_cat = set()
        r_cat = set()
        l_cat = l_cat.union(fetchSet(l, 'Product Type'), fetchSet(l, 'Category'))
        r_cat = r_cat.union(fetchSet(r, 'Product Type'), fetchSet(r, 'Category'))
        return py_stringmatching.simfunctions.tfidf(l_cat, r_cat)

    def color_match(self, l, r):
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

        if 'Product Short Description' in l:
            l_color = l_color.union(self.ie.color_from_name(l['Product Short Description'][0]))
        if 'Product Short Description' in r:
            r_color = r_color.union(self.ie.color_from_name(r['Product Short Description'][0]))
        return py_stringmatching.simfunctions.jaccard(l_color, r_color)

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
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)

    def getVector(self, l, r):
        #initialize vector and empty lld and rld (left long descript, right long descript)
        rld = {}
        lld = {}
        vector = []

        #parse html in long descriptions, if any
        if pld in l.keys():
            self.parser.result = {}
            self.parser.feed(l[pld][0])
            lld = self.parser.result
        if pld in r.keys():
            self.parser.result = {}
            self.parser.feed(r[pld][0])
            rld = self.parser.result

        # functions that do not take in long description dictionaries
        for func in self.is_stress_test, self.product_long_description_tfidf, self.product_long_description_jaccard, self.product_type_tfidf, self.product_type_jaccard, self.product_segment_tfidf, self.product_segment_jaccard, self.assembled_product_length_jaccard, self.assembled_product_width_jaccard, self.product_name_jaccard, self.product_name_tfidf, self.brand_name_sim, self.color_match, self.product_short_description_tfidf, self.product_short_description_jaccard, self.category_match, self.big_text_tfidf:
            x = func(l, r)
            vector.append(x)

        # functions that do
        for func in self.long_descript_key_sim, self.total_key_similarity, self.manufacturer_jaccard, self.manufacturer_part_number_jaccard:
            y = func(l, r, lld, rld)
            vector.append(y)

        return vector
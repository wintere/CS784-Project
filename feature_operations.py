__author__ = 'wintere'

import py_stringmatching.tokenizers
import py_stringmatching.simfunctions
from information_extraction import InformationExtractor

#Rules to nest in:
#always return MISMATCH or FALSE if 'stress testing DO NOT BUY' in product name
#as these are not real products

#helper method
def fetchSet(dict, key):
    if key not in dict:
        return []
    else:
        return dict[key]

class FeatureGenerator:
    def __init__(self):
        self.ie = InformationExtractor()
        self.syn_dict = self.ie.syn_dict

    def product_name_jaccard(self, d1, d2):
        p1 = d1.get('Product Name')[0]
        p2 = d2.get('Product Name')[0]
        p1_tokens = py_stringmatching.tokenizers.whitespace(p1)
        p2_tokens = py_stringmatching.tokenizers.whitespace(p2)
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def product_name_tfidf(self,d1, d2):
        p1 = d1.get('Product Name')[0]
        p2 = d2.get('Product Name')[0]
        p1_tokens = py_stringmatching.tokenizers.whitespace(p1)
        p2_tokens = py_stringmatching.tokenizers.whitespace(p2)
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)


    def product_short_description_tfidf(self, d1, d2):
        p1_tokens = []
        p2_tokens = []
        p1 = d1.get('Product Short Description')
        p2 = d2.get('Product Short Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)



    def product_long_description_tfidf(self,d1, d2):
        p1_tokens = []
        p2_tokens = []
        p1 = d1.get('Product Long Description')
        p2 = d2.get('Product Long Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)
        
    def product_type_tfidf(self,d1, d2):
        p1_tokens = []
        p2_tokens = []
        p1 = d1.get('Product Type')
        p2 = d2.get('Product Type')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)
        
    def product_segment_tfidf(self,d1, d2):
        p1_tokens = []
        p2_tokens = []
        p1 = d1.get('Product Segment')
        p2 = d2.get('Product Segment')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)

    def brand_name_sim(self,d1, d2):
        p1 = d1.get('Brand')
        p2 = d2.get('Brand')
        if p1 is None:
            p1 = self.ie.brand_from_string(d1.get('Product Name')[0])
        else:
            p1 = p1[0]
            if p1 in self.syn_dict:
                p1 = self.syn_dict[p1]
        if p2 is None:
            p2 = self.ie.brand_from_string(d2.get('Product Name')[0])
        else:
            p2 = p2[0]
            if p2 in self.syn_dict:
                p2 = self.syn_dict[p2]
        return py_stringmatching.simfunctions.jaro_winkler(p1, p2)

    def category_match(self, d1, d2):
        d1_cat = set()
        d2_cat = set()
        d1_cat = d1_cat.union(fetchSet(d1, 'Product Type'), fetchSet(d1, 'Category'))
        d2_cat = d2_cat.union(fetchSet(d2, 'Product Type'), fetchSet(d2, 'Category'))
        return py_stringmatching.simfunctions.tfidf(d1_cat, d2_cat)

    def color_match(self, d1, d2):
        d1_color = set()
        d2_color = set()
        # step 1: try it the easy way
        if 'Color' in d1:
            d1_color.add(d1['Color'][0])
        elif 'Actual Color' in d1:
            d1_color.add(d1['Actual Color'][0])
        if 'Color' in d2:
            d2_color.add(d2['Color'][0])
        elif 'Actual Color' in d2:
            d2_color.add(d2['Actual Color'][0])
        # add colors in product name
        d1_name = d1.get('Product Name')[0]
        d1_color = d1_color.union(self.ie.color_from_name(d1_name))
        d2_name = d2.get('Product Name')[0]
        d2_color = d2_color.union((self.ie.color_from_name(d2_name)))

        if 'Product Short Description' in d1:
            d1_color = d1_color.union(self.ie.color_from_name(d1['Product Short Description'][0]))
        if 'Product Short Description' in d2:
            d2_color = d2_color.union(self.ie.color_from_name(d2['Product Short Description'][0]))
        return py_stringmatching.simfunctions.jaccard(d1_color, d2_color)



    def getVector(self, d1, d2):
        vector = []
        for func in self.product_long_description_tfidf, self.product_type_tfidf, self.product_segment_tfidf, self.product_name_jaccard, self.product_name_tfidf, self.brand_name_sim, self.color_match, self.product_short_description_tfidf, self.category_match:
            x = func(d1, d2)
            vector.append(x)
        return vector
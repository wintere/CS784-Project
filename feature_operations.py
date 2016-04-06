__author__ = 'wintere'

import py_stringmatching.tokenizers
import py_stringmatching.simfunctions
from information_extraction import InformationExtractor

#Rules to nest in:
#always return MISMATCH or FALSE if 'stress testing DO NOT BUY' in product name
#as these are not real products

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

    def product_long_description_jaccard(self,d1, d2):
        p1_tokens = []
        p2_tokens = []
        p1 = d1.get('Product Long Description')
        p2 = d2.get('Product Long Description')
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

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
        p1_tokens = py_stringmatching.tokenizers.whitespace(p1)
        p2_tokens = py_stringmatching.tokenizers.whitespace(p2)
        return py_stringmatching.simfunctions.monge_elkan(p1_tokens, p2_tokens)


    def getVector(self, d1, d2):
        vector = []
        for func in self.product_long_description_jaccard, self.product_name_jaccard, self.brand_name_sim:
            x = func(d1, d2)
            vector.append(x)
        return vector
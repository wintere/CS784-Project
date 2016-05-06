__author__ = 'wintere'

import py_stringmatching.tokenizers
import py_stringmatching.simfunctions
from information_extraction import InformationExtractor
from html_parser import MyHtmlParser
import re
import math

pld = 'product long description'
psd = 'product short description'

stops = ['-', '.', '\n', '', '&', 'and','this','with','the', 'you', 'to', 'a', 'an', 'or', 'have', 'should', 'more']

def tokenizeAndFilter(string):
    tokens = []
    toks = re.split(r'[ \|\[\]\_,\/\(\)\*\n\t\b\r\{\}\~\;\!\:]', string)
    for i in toks:
        if i not in stops:
            tokens.append(i)
    return (tokens)

def cleanTokenize(string):
    tokens = []
    toks = re.split(r'[ \|\[\]_,\/\(\)\*\n\t\b\r\{\}\~\;\!\:]', string)
    for i in toks:
        if i != '' and i != '\n' and i != '-':
            tokens.append(i)
    return(tokens)

#helper method
def fetchSet(dict, key):
    if key not in dict:
        return []
    val = dict[key]
    if isinstance(val, str):
        return [val]
    else:
        return val


# helper method adapted from py_stringmatching tfidf source code
def pystr_idf(l_tokens, r_tokens, dictionary):
    total = set(l_tokens).union(set(r_tokens))
    tfidf_d = dictionary
    v_x_y = 0
    v_x_2 = 0
    v_y_2 = 0
    for word in total:
        v_x = 0
        v_y = 0
        if (word in l_tokens) and (word in tfidf_d):
            tfidf = tfidf_d[word] * l_tokens.count(word)
            if tfidf == 0:
                tfidf = 0.0001
            v_x = math.log(tfidf)
        if (word in r_tokens) and (word in tfidf_d):
            tfidf = tfidf_d[word] * r_tokens.count(word)
            if tfidf == 0:
                tfidf = 0.0001
            v_y = math.log(tfidf)
        v_x_y += v_x * v_y
        v_x_2 += v_x * v_x
        v_y_2 += v_y * v_y
    return 0.0 if v_x_y == 0 else v_x_y / (math.sqrt(v_x_2) * math.sqrt(v_y_2))

class FeatureGenerator:
    def __init__(self):
        self.ie = InformationExtractor()
        self.parser = MyHtmlParser()
        #adjust functions here to keep labels
        self.syn_dict = self.ie.syn_dict


        #no long description dictionary arguments
        self.lr_functions = self.product_long_description_tfidf, self.big_text_tfidf, self.product_long_description_jaccard, self.product_name_jaccard,

        #long dictionary arguments
        self.longd_functions = self.long_descript_key_sim, self.total_key_similarity, self.color_match, self.manufacturer_jaccard, self.brand_and_brand_name_sim,  self.category_sim, self.assembled_product_length_sim, self.assembled_product_width_sim, self.product_line_jaccard, self.model_levenshtein, self.weight_jaccard,self.depth_jaccard, self.product_short_description_jaccard,self.product_name_monge_elkan,self.product_name_measurements_jaccard



        # for log regression
        self.all_lr_functions = self.big_text_tfidf, self.big_text_jaccard, self.product_long_description_jaccard, self.product_name_jaccard, self.impromptu_longd_tfidf, self.product_name_tfidf, self.product_long_description_measurements, self.big_text_shared_keys_tfidf,
        self.all_longd_functions = self.assembled_product_length_sim, self.assembled_product_width_sim, self.assembly_code_sim, self.brand_and_brand_name_sim, self.color_match, self.depth_jaccard, self.device_type_sim, self.form_factor_jaccard, self.green_compliant_jaccard, self.green_indicator_sim, self.manufacturer_jaccard, self.manufacturer_part_number_jaccard, self.model_levenshtein, self.operating_system_jaccard, self.processor_core_levenshtein, self.product_line_jaccard, self.product_model_levenshtein, self.product_series_jaccard, self.product_type_sim, self.screen_size_jaccard, self.total_key_similarity, self.type_jaccard, self.weight_jaccard, self.width_jaccard, self.product_short_description_jaccard, self.product_short_description_tfidf,self.big_text_no_pld_jaccard, self.key_length_difference, self.ld_key_length_difference, self.product_name_monge_elkan,self.product_name_measurements_jaccard, self.conditionmatch, self.big_text_overlap_coeffecient, self.product_segment_jaccard


    def impromptu_longd_tfidf(self, l, r):
        p1 = l.get(pld)
        p2 = r.get(pld)
        tf_x = []
        tf_y = []
        if p1 is not None:
            tf_x = (cleanTokenize(p1[0]))
        if p2 is not None:
            tf_y = (cleanTokenize(p2[0]))
        return pystr_idf(tf_x, tf_y, self.ie.longd_tfidf)

    def product_name_tfidf(self, l, r):
        p1 = l.get('product name')[0]
        p2 = r.get('product name')[0]
        tf_x = (cleanTokenize(p1))
        tf_y = (cleanTokenize(p2))
        return pystr_idf(tf_x, tf_y, self.ie.pname_tfidf)

    #checked
    def product_name_jaccard(self, l, r):
        p1 = l.get('product name')[0]
        p2 = r.get('product name')[0]
        p1_tokens = tokenizeAndFilter(p1)
        p2_tokens = tokenizeAndFilter(p2)
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #checked
    def product_name_monge_elkan(self,l, r, lld, rld):
        p1_tok = []
        p2_tok = []
        p1 = l.get('product name')[0].lower()
        p2 = r.get('product name')[0].lower()
        p1_tok.extend(tokenizeAndFilter(p1))
        p2_tok.extend(tokenizeAndFilter(p2))
        if 'product name' in lld:
            p1_tok.extend(tokenizeAndFilter(lld['product name'].lower()))
        if 'product name' in rld:
            p2_tok.extend(tokenizeAndFilter(rld['product name'].lower()))
        return py_stringmatching.simfunctions.monge_elkan(p1_tok, p2_tok)

    def key_length_difference(self, l, r, lld, rld):
        l_keys = list(l.keys())
        r_keys = list(r.keys())
        return (abs(len(l_keys) - len(r_keys)))/(len(l_keys) + len(r_keys))

    def ld_key_length_difference(self, l, r, lld, rld):
        lld_keys = list(lld.keys())
        rld_keys = list(rld.keys())
        if len(lld_keys) > 0 or len(rld_keys) > 0:
            return (abs(len(lld_keys) - len(rld_keys)))/(len(lld_keys) + len(rld_keys))
        else:
            return 0

    #checked
    def product_short_description_tfidf(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get(psd)
        p2 = r.get(psd)
        if p1 is None and psd in lld:
            p1 = lld.get(psd)
        if p2 is None and psd in rld:
            p2 = rld.get(psd)
        if p1 is not None:
            p1_tokens = cleanTokenize(p1[0])
        if p2 is not None:
            p2_tokens = cleanTokenize(p2[0])
            
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens, dampen=True)

    #checked
    def product_short_description_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('product short description')
        p2 = r.get('product short description')
        if p1 is None and psd in lld:
            p1 = lld.get(psd)
        if p2 is None and psd in rld:
            p2 = rld.get(psd)
        if p1 is not None:
            p1_tokens = tokenizeAndFilter(p1[0])
        if p2 is not None:
            p2_tokens = tokenizeAndFilter(p2[0])
        
        # if this field does not exist in one of the tuples, then this data is inconclusive. return 0.5.
        if (p1_tokens and not p2_tokens) or (p2_tokens and not p1_tokens):
            return 0.5
        
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #checked
    def total_key_similarity(self, l, r, lld, rld):
        l_keys = list(l.keys())
        r_keys = list(r.keys())
        l_keys = [x.lower() for x in l_keys]
        r_keys = [x.lower() for x in r_keys]
        return py_stringmatching.simfunctions.overlap_coefficient(set(l_keys), set(r_keys))


    #checked
    def long_descript_key_sim(self, l, r, lld, rld):
        lld_keys = list(lld.keys())
        rld_keys = list(rld.keys())
        lld_keys = [x.lower() for x in lld_keys]
        rld_keys = [x.lower() for x in rld_keys]
        return py_stringmatching.simfunctions.overlap_coefficient(lld_keys, rld_keys)

    #checked
    def product_long_description_tfidf(self,l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('product long description')
        p2 = r.get('product long description')
        if p1 is not None:
            p1_tokens = cleanTokenize(p1[0])
        if p2 is not None:
            p2_tokens = cleanTokenize(p2[0])
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens, dampen=True)

    #checked
    def product_long_description_jaccard(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('product long description')
        p2 = r.get('product long description')
        if p1 is not None:
            p1_tokens = tokenizeAndFilter(p1[0])
        if p2 is not None:
            p2_tokens = tokenizeAndFilter(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #checked
    def product_type_sim(self,l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1_tokens.extend(fetchSet(l,'product type'))
        p1_tokens.extend(fetchSet(lld, 'product type'))
        p2_tokens.extend(fetchSet(r,'product type'))
        p2_tokens.extend(fetchSet(rld, 'product type'))
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #checked
    def product_segment_jaccard(self,l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('product segment')
        p2 = r.get('product segment')
        if p1 is None and 'product segment' in lld.keys():
            p1 = [lld.get('product segment')]
        if p2 is None and 'product segment' in rld.keys():
            p2 = [rld.get('product segment')]
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #checked
    def manufacturer_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('manufacturer')
        p2 = r.get('manufacturer')

        # if these fields don't exist in the main key-value set, then check the parsed product long description data.
        if p1 is None and 'manufacturer' in lld.keys():
            p1 = [lld.get('manufacturer')]
        if p2 is None and 'manufacturer' in rld.keys():
            p2 = [rld.get('manufacturer')]

        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        
        return py_stringmatching.simfunctions.monge_elkan(p1_tokens, p2_tokens)

    #string distance instead?
    def manufacturer_part_number_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('manufacturer part number')
        p2 = r.get('manufacturer part number')

        # if these fields don't exist in the main key-value set, then check the parsed product long description data.
        if p1 is None and 'manufacturer part number' in lld.keys():
            p1 = [lld.get('manufacturer part number')]
        if p2 is None and 'manufacturer part number' in rld.keys():
            p2 = [rld.get('manufacturer part number')]

        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #checked
    def assembled_product_length_sim(self, l, r, lld, rld):
        p1 = ''
        p2 = ''
        if 'assembled product length' in l:
            p1 = l.get('assembled product length')[0]
        if 'assembled product length' in r:
            p2 = r.get('assembled product length')[0]
        if p1 is '' and 'assembled product length' in lld:
            p1 = lld.get('assembled product length')
        if p2 is '' and 'assembled product length' in rld:
            p2 = rld.get('assembled product length')
        y = max(len(p1), len(p2))
        if y > 0:
            return py_stringmatching.simfunctions.levenshtein(p1, p2)/y
        return 1

    #checked
    def assembled_product_width_sim(self, l, r, lld, rld):
        p1 = ''
        p2 = ''
        if 'assembled product width' in l:
            p1 = l.get('assembled product width')[0]
        if 'assembled product width' in r:
            p2 = r.get('assembled product width')[0]
        if p1 is '' and 'assembled product width' in lld:
            p1 = lld.get('assembled product width')
        if p2 is '' and 'assembled product width' in rld:
            p2 = rld.get('assembled product width')
        y = max(len(p1), len(p2))
        if y > 0:
            return py_stringmatching.simfunctions.levenshtein(p1, p2)/y
        return 1

    #checked
    def color_match(self, l, r, lld, rld):
        l_color = set()
        r_color = set()
        # step 1: try it the easy way
        if 'color' in l:
            l_color.add(l['color'][0])
        elif 'actual color' in l:
            l_color.add(l['actual color'][0])
        if 'color' in r:
            r_color.add(r['color'][0])
        elif 'actual color' in r:
            r_color.add(r['actual color'][0])
        # add colors in product name
        l_name = l.get('product name')[0]
        l_color = l_color.union(self.ie.color_from_name(l_name))
        r_name = r.get('product name')[0]
        r_color = r_color.union(self.ie.color_from_name(r_name))
        if 'color' in lld:
            l_color = l_color.union(fetchSet(lld, 'color'))
        if 'color' in rld:
            r_color = r_color.union(fetchSet(rld, 'color'))
        l_color = set([x.lower() for x in l_color])
        r_color = set([x.lower() for x in r_color])
        return py_stringmatching.simfunctions.jaccard(l_color, r_color)

    def big_text_shared_keys_tfidf(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1_keys = l.keys()
        p2_keys = r.keys()
        all_keys = set(p1_keys).intersection(set(p2_keys))
        for key in all_keys:
            p1_tokens.extend(tokenizeAndFilter(l.get(key)[0]))
            p2_tokens.extend(tokenizeAndFilter(r.get(key)[0]))
        s = py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens)
        return s

    #checked
    def big_text_jaccard(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1_keys = l.keys()
        p2_keys = r.keys()
        for key in p1_keys:
            p1_tokens.extend(cleanTokenize(key))
            p1_tokens.extend(tokenizeAndFilter(l.get(key)[0]))
        for key in p2_keys:
            p2_tokens.extend(cleanTokenize(key))
            p2_tokens.extend(tokenizeAndFilter(r.get(key)[0]))
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def big_text_no_pld_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1_keys = l.keys()
        p2_keys = r.keys()
        p1_more_keys = lld.keys()
        p2_more_keys = rld.keys()
        for key in p1_keys:
            if key != 'product long description':
                p1_tokens.extend(cleanTokenize(key))
                p1_tokens.extend(tokenizeAndFilter(l.get(key)[0]))
        for key in p2_keys:
            if key != 'product long description':
                p2_tokens.extend(cleanTokenize(key))
                p2_tokens.extend(tokenizeAndFilter(r.get(key)[0]))
        for key in p1_more_keys:
            if key != 'product long description' and key not in p1_keys:
                p1_tokens.extend(cleanTokenize(key))
                p1_tokens.extend(tokenizeAndFilter(lld.get(key)))
        for key in p2_more_keys:
            if key != 'product long description' and key not in p2_keys:
                p2_tokens.extend(cleanTokenize(key))
                p2_tokens.extend(tokenizeAndFilter(rld.get(key)))
        return py_stringmatching.simfunctions.overlap_coefficient(p1_tokens, p2_tokens)

    def big_text_overlap_coeffecient(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1_keys = l.keys()
        p2_keys = r.keys()
        p1_more_keys = lld.keys()
        p2_more_keys = rld.keys()
        for key in p1_keys:
            p1_tokens.extend(tokenizeAndFilter(l.get(key)[0]))
        for key in p2_keys:
            p2_tokens.extend(tokenizeAndFilter(r.get(key)[0]))
        for key in p1_more_keys:
            p1_tokens.extend(tokenizeAndFilter(lld.get(key)))
        for key in p2_more_keys:
            p2_tokens.extend(tokenizeAndFilter(rld.get(key)))
        ret = py_stringmatching.simfunctions.overlap_coefficient(p1_tokens, p2_tokens)
        return ret

    def all_key_value_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1_keys = l.keys()
        p2_keys = r.keys()
        p1_more_keys = lld.keys()
        p2_more_keys = rld.keys()
        for key in p1_keys:
            p1_tokens.extend(str(key + ':' + l.get(key)[0]))
        for key in p2_keys:
            p2_tokens.extend(str(key + ':' + r.get(key)[0]))
        for key in p1_more_keys:
            if key not in p1_keys:
                p1_tokens.extend(str(key + ':' + lld.get(key)))
        for key in p2_more_keys:
            if key not in p2_keys:
                p2_tokens.extend(str(key + ':' + rld.get(key)))
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    #checked
    def big_text_tfidf(self, l, r):
        p1_tokens = []
        p2_tokens = []
        p1_keys = l.keys()
        p2_keys = r.keys()
        for key in p1_keys:
            p1_tokens.extend(cleanTokenize(l.get(key)[0]))
        for key in p2_keys:
            p2_tokens.extend(cleanTokenize(r.get(key)[0]))
        return py_stringmatching.simfunctions.tfidf(p1_tokens, p2_tokens, dampen=True)

    #checked
    def brand_and_brand_name_sim(self, l, r, lld, rld):
        p1 = ''
        p2 = ''
        if 'brand' in l:
            p1 = l.get('brand')[0]
        if 'brand' in r:
            p2 = r.get('brand')[0]
        if p1 is '' and 'brand name' in l.keys():
            p1 = l.get('brand name')[0]
        if p2 is '' and 'brand name' in r.keys():
            p2 = r.get('brand name')[0]
        if p1 is '' and 'brand' in lld.keys():
            p1 = lld.get('brand')
        if p2 is '' and 'brand' in rld.keys():
            p2 = rld.get('brand')
        if p1 is '' and 'brand name' in lld.keys():
            p1 = lld.get('brand name')
        if p2 is '' and 'brand name' in rld.keys():
            p2 = rld.get('brand name')

        #last attempt: try information extraction
        if p1 is '':
            p1 = self.ie.brand_from_string(l.get('product name')[0])
        if p2 is '':
            p2 = self.ie.brand_from_string(r.get('product name')[0])

        #standardize extracted brands
        if p1.upper() in self.ie.syn_dict:
            p1 = self.ie.syn_dict[p1.upper()]
        if p2.upper() in self.ie.syn_dict:
            p2 = self.ie.syn_dict[p2.upper()]

        return py_stringmatching.simfunctions.jaro(p1.lower(), p2.lower())

    def limited_warranty_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('limited warranty')
        p2 = r.get('limited warranty')
        if p1 is None and 'limited warranty' in lld.keys():
            p1 = [lld.get('limited warranty')]
        if p2 is None and 'limited warranty' in rld.keys():
            p2 = [rld.get('limited warranty')]
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def weight_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('weight')
        p2 = r.get('weight')
        if p1 is None and 'weight' in lld.keys():
            p1 = [lld.get('weight')]
        if p2 is None and 'weight' in rld.keys():
            p2 = [rld.get('weight')]
        if p1 is None and 'weight (approximate)' in l:
            p1 = l.get('weight (approximate)')
        if p2 is None and 'weight (approximate)' in r:
            p2 = r.get('weight (approximate)')
        if p1 is None and 'weight (approximate)' in lld.keys():
            p1 = [lld.get('weight (approximate)')]
        if p2 is None and 'weight (approximate)' in rld.keys():
            p2 = [rld.get('weight (approximate)')]
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0].lower())
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0].lower())
            
        # if this field does not exist in one of the tuples, then this data is inconclusive. return 0.5.
        if (p1_tokens and not p2_tokens) or (p2_tokens and not p1_tokens):
            return 0.5
        
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def width_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('width')
        p2 = r.get('width')
        if p1 is None and 'width' in lld.keys():
            p1 = [lld.get('width')]
        if p2 is None and 'width' in rld.keys():
            p2 = [rld.get('width')]     
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
            
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def depth_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('depth')
        p2 = r.get('depth')
        if p1 is None and 'depth' in lld.keys():
            p1 = [lld.get('depth')]
        if p2 is None and 'depth' in rld.keys():
            p2 = [rld.get('depth')]     
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
           
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def product_series_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('product series')
        p2 = r.get('product series')
        if p1 is None and 'product series' in lld.keys():
            p1 = [lld.get('product series')]
        if p2 is None and 'product series' in rld.keys():
            p2 = [rld.get('product series')]     
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        p1_tokens = [x.lower() for x in p1_tokens]
        p2_tokens = [x.lower() for x in p2_tokens]
        
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def features_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('features')
        p2 = r.get('features')
        if p1 is None and 'features' in lld.keys():
            p1 = [lld.get('features')]
        if p2 is None and 'features' in rld.keys():
            p2 = [rld.get('features')]     
        if p1 is not None:
            p1_tokens = cleanTokenize(p1[0])
        if p2 is not None:
            p1_tokens = cleanTokenize(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def product_line_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('product line')
        p2 = r.get('product line')
        if p1 is None and 'product line' in lld.keys():
            p1 = [lld.get('product line')]
        if p2 is None and 'product line' in rld.keys():
            p2 = [rld.get('product line')]     
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def screen_size_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('screen size')
        p2 = r.get('screen size')
        if p1 is None and 'screen size' in lld.keys():
            p1 = [lld.get('screen size')]
        if p2 is None and 'screen size' in rld.keys():
            p2 = [rld.get('screen size')]     
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def green_compliant_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('green compliant')
        p2 = r.get('green compliant')
        if p1 is None and 'green compliant' in lld.keys():
            p1 = [lld.get('green compliant')]
        if p2 is None and 'green compliant' in rld.keys():
            p2 = [rld.get('green compliant')]     
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def type_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('type')
        p2 = r.get('type')
        if p1 is None and 'type' in lld.keys():
            p1 = [lld.get('type')]
        if p2 is None and 'type' in rld.keys():
            p2 = [rld.get('type')]
        if p1 is not None:
            p1_tokens = cleanTokenize(p1[0])
        if p2 is not None:
            p2_tokens = cleanTokenize(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def form_factor_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('form factor')
        p2 = r.get('form factor')
        if p1 is None and 'form factor' in lld.keys():
            p1 = [lld.get('form factor')]
        if p2 is None and 'form factor' in rld.keys():
            p2 = [rld.get('form factor')]     
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)

    def operating_system_jaccard(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('operating system')
        p2 = r.get('operating system')
        if p1 is None and 'operating system' in lld.keys():
            p1 = [lld.get('operating system')]
        if p2 is None and 'operating system' in rld.keys():
            p2 = [rld.get('operating system')]     
        if p1 is not None:
            p1_tokens = py_stringmatching.tokenizers.whitespace(p1[0])
        if p2 is not None:
            p2_tokens = py_stringmatching.tokenizers.whitespace(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)


    def category_sim(self, l, r, lld, rld):
        p1_tokens = []
        p2_tokens = []
        p1 = l.get('category')
        p2 = r.get('category')
        if p1 is None and 'category' in lld.keys():
            p1 = [lld.get('category')]
        if p2 is None and 'category' in rld.keys():
            p2 = [rld.get('category')]
        if p1 is not None:
            p1_tokens = cleanTokenize(p1[0])
        if p2 is not None:
            p1_tokens = cleanTokenize(p2[0])
        return py_stringmatching.simfunctions.jaccard(p1_tokens, p2_tokens)
        
    def assembly_code_sim(self, l, r, lld, rld):
        p1 = l.get('assembly code')
        p2 = r.get('assembly code')
        if p1 is None and 'assembly code' in lld.keys():
            p1 = [lld.get('assembly code')]
        if p2 is None and 'assembly code' in rld.keys():
            p2 = [rld.get('assembly code')]     
        if p1 is None:
            p1 = [""]
        if p2 is None:
            p2 = [""]
        y = max(len(p1),len(p2))
        if y > 0:
            return py_stringmatching.simfunctions.levenshtein(p1[0], p2[0])/y
        if p1 != "" or p2 != "":
            return 1
        return 0

    def green_indicator_sim(self, l, r, lld, rld):
        p1 = l.get('green indicator')
        p2 = r.get('green indicator')
        if p1 is None and 'green indicator' in lld.keys():
            p1 = [lld.get('green indicator')]
        if p2 is None and 'green indicator' in rld.keys():
            p2 = [rld.get('green indicator')]     
        if p1 is None:
            p1 = [""]
        if p2 is None:
            p2 = [""]
        y = max(len(p1),len(p2))
        if y > 0:
            return py_stringmatching.simfunctions.levenshtein(p1[0], p2[0])/y
        if p1 != "" or p2 != "":
            return 1
        return 0

    def model_levenshtein(self, l, r, lld, rld):
        p1 = l.get('model')
        p2 = r.get('model')
        if p1 is None and 'model' in lld.keys():
            p1 = [lld.get('model')]
        if p2 is None and 'model' in rld.keys():
            p2 = [rld.get('model')]     
        if p1 is None:
            p1 = [""]
        if p2 is None:
            p2 = [""]
        y = max(len(p1),len(p2))
        if y > 0:
            return py_stringmatching.simfunctions.levenshtein(p1[0], p2[0])/y
        if p1 != "" or p2 != "":
            return 1
        return 0

    #fixed (remember edit distance is not automatically divided by length of string, hence it can be as large as the length of the string)
    def product_model_levenshtein(self, l, r, lld, rld):
        p1 = l.get('product model')
        p2 = r.get('product model')
        if p1 is None and 'product model' in lld.keys():
            p1 = [lld.get('product model')]
        if p2 is None and 'product model' in rld.keys():
            p2 = [rld.get('product model')]     
        if p1 is None:
            p1 = [""]
        if p2 is None:
            p2 = [""]
        y = max(len(p1),len(p2))
        if y > 0:
            return py_stringmatching.simfunctions.levenshtein(p1[0].lower(), p2[0].lower())/y
        if p1 != "" or p2 != "":
            return 0.5
        return 0

    # this only appears in 27 tuples it's probably not actually useful
    def processor_core_levenshtein(self, l, r, lld, rld):
        p1 = l.get('processor core')
        p2 = r.get('processor core')
        if p1 is None and 'processor core' in lld.keys():
            p1 = [lld.get('processor core')]
        if p2 is None and 'processor core' in rld.keys():
            p2 = [rld.get('processor core')]     
        if p1 is None:
            p1 = [""]
        if p2 is None:
            p2 = [""]
        y = max(len(p1),len(p2))
        if y > 0:
            return py_stringmatching.simfunctions.levenshtein(p1[0].lower(), p2[0].lower())/y
        if p1 != "" or p2 != "":
            return 0.5
        return 0

    def device_type_sim(self, l, r, lld, rld):
        #synonyms
        dt = 'device type'
        ds = 'device types'
        p1 = set()
        p2 = set()
        p1 = p1.union(fetchSet(l, dt), fetchSet(lld, dt), fetchSet(l, ds), fetchSet(lld, ds))
        p2 = p2.union(fetchSet(r, dt), fetchSet(rld, dt), fetchSet(r, ds), fetchSet(rld, ds))
        r =  py_stringmatching.simfunctions.monge_elkan(p1, p2)
        return r

    def product_long_description_measurements(self, l, r):
        p1_tok = []
        p2_tok = []
        p1 = l.get(pld)
        p2 = r.get(pld)
        if p1 is not None:
            p1_tok.extend(cleanTokenize(p1[0]))
        if p2 is not None:
            p2_tok.extend(cleanTokenize(p2[0]))

        p1_measurements = set(self.ie.unitsFromString(p1_tok))
        p2_measurements = set(self.ie.unitsFromString(p2_tok))

        jaccard_value = py_stringmatching.simfunctions.jaccard(p1_measurements, p2_measurements)
        # if only one tuple returned valid measurements, return 0.5 (since this is inconclusive)
        if (p1_measurements and not p2_measurements) or (p2_measurements and not p1_measurements):
            jaccard_value = 0.5
        return jaccard_value

    def product_name_measurements_jaccard(self,l, r, lld, rld):
        p1_tok = []
        p2_tok = []
        p1 = l.get('product name')[0]
        p2 = r.get('product name')[0]
        p1_tok.extend(cleanTokenize(p1))
        p2_tok.extend(cleanTokenize(p2))

        p1_units = set(self.ie.unitsFromString(p1_tok))
        p2_units = set(self.ie.unitsFromString(p2_tok))
        jaccard_value = py_stringmatching.simfunctions.jaccard(p1_units, p2_units)
        # if only one tuple returned valid units, return 0.5 (since this is inconclusive)
        if (p1_units and not p2_units) or (p2_units and not p1_units):
            jaccard_value = 0.5
        return jaccard_value

    def conditionmatch(self, l, r, lld, rld):
        p1 = set()
        p2 = set()
        pc = 'product condition'
        c = 'condition'
        p1 = p1.union(fetchSet(l, c), fetchSet(lld, c), fetchSet(l, pc), fetchSet(lld, pc))
        p2 = p2.union(fetchSet(r, c), fetchSet(rld, c), fetchSet(r, pc), fetchSet(rld, pc))
        if p1 is None:
            if pld in p1 and ('refurbished' in p1[pld][0] or 'refurbished' in (p1['product name'][0]).lower()):
                p1 = set('refurbished')
        if p2 is None:
            if pld in p2 and ('refurbished' in p2[pld][0] or 'refurbished' in (p2['product name'][0]).lower()):
                p2 = set('refurbished')
        if p1 != p2:
            return 0
        else:
            return 1


    def getVectorAttributes(self, allFuncs=False):
        att = []
        if allFuncs:
            lr_functions = self.all_lr_functions
            longd_functions = self.all_longd_functions
        else:
            lr_functions = self.lr_functions
            longd_functions = self.all_longd_functions

        for func in lr_functions:
            str = func.__name__
            att.append(str)

        # functions that do
        for func in longd_functions:
            str = func.__name__
            att.append(str)
        return att

    def getVector(self, l, r, allFuncs=False):
        rld = {}
        lld = {}
        vector = []

        #parse html in long descriptions, if any
        if pld in l.keys():
            self.parser.reset()
            self.parser.result = {}
            self.parser.feed(l[pld][0])
            lld = self.parser.result
            l[pld] = [self.ie.text_from_html(l[pld][0])]
        if pld in r.keys():
            self.parser.reset()
            self.parser.result = {}
            self.parser.feed(r[pld][0])
            rld = self.parser.result
            r[pld] = [self.ie.text_from_html(r[pld][0])]
        for dict in [l,r]:
            for key in dict.keys():
                v = dict[key]
                if "<" in v[0] or ">" in v[0]:
                    dict[key] = [self.ie.text_from_html(v[0])]
        if psd in l:
            l[psd] = [self.ie.text_from_html(l[psd][0])]
        if psd in r:
            r[psd] = [self.ie.text_from_html(r[psd][0])]

        l = self.ie.brand_adjuster(l)
        r = self.ie.brand_adjuster(r)

        if allFuncs:
            lr_functions = self.all_lr_functions
            longd_functions = self.all_longd_functions
        else:
            lr_functions = self.lr_functions
            longd_functions = self.longd_functions
        # functions that do not take in long description dictionaries
        for func in lr_functions:
            x = func(l, r)
            vector.append(x)

        # functions that do
        for func in longd_functions:
            y = func(l, r, lld, rld)
            vector.append(y)
        return vector
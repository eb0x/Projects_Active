# !/usr/bin/python

#Take all the BNC text files and pickle then into a word_dict

import os

from os.path import isfile, join
import re
import sys
import csv
import pickle
import math
import time
import numpy as np
import nltk.data
from nltk.tokenize import sent_tokenize,  word_tokenize, TreebankWordTokenizer
from nltk.tag import pos_tag_sents, pos_tag
#from nltk.corpus import stopwords                    #Current policy -- no stemming, lemmatizing or stops
#from nltk.stem.snowball import SnowballStemmer
import string, timeit

from CM0645db import Db

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # use punkt English Tokenizer
translator = str.maketrans('', '', string.punctuation)
#stemmer = SnowballStemmer("english")

class Process_BNC:

    def __init__(self, sourcedir, reprocess=False):
        self.sourcedir = sourcedir
        if reprocess:
            self.word_dict = {}
            self.process_all()
        else:
            self.loadBNC("BNC.pickle")


    def process_all(self):
        for root, dirs, files in os.walk(self.sourcedir, topdown=True):
            for name in files:
                fname = os.path.join(root, name)
                print("File:", fname)
                with open(fname) as f:
                    content = f.read()
                    sent_tokenize_list = sent_tokenize(content )   #split into sentences 
                    self.record_BNC_stats(sent_tokenize_list)
            for name in dirs:
                print("Dir:", os.path.join(root, name))


    def record_BNC_stats(self, sent_tokenize_list):
        token_count = 0
        word_dict = self.word_dict
        for line in sent_tokenize_list:
            words = word_tokenize(line)
            # print("line: ", line, " words:", words)
            for word in words:
                word = word.lower().translate(translator)
                if word:
                    token_count += 1
                    if word in word_dict:
                        word_dict[word] += 1
                    else:
                        word_dict[word] = 1
        self.word_dict = word_dict

        #Used as a trial to see if worthwhile calculating this in advance over the BNC (No -- takes 0.25secs)
    def CalcIDF(self):
        unique_terms = len(self.word_dict.keys()) 
        total_tokens = sum(self.word_dict.values())
        start = time.time()
        for term, freq in self.word_dict.items():
#            print(k, 'corresponds to', v)
            self.word_dict[term] = math.log(total_tokens/freq)
        end = time.time()
        print("Calculating IDF  took {} seconds".format(end - start) )

            
    def saveBNC(self, outfile):
        with open(outfile, "wb") as myFile:
            pickle.dump(self.word_dict, myFile)

    def loadBNC(self, infile):
        print("BNC File: ", infile)
        BNCdict =  pickle.load(open( infile, "rb" ))
        self.word_dict = BNCdict

    def describe(self):
        unique_terms = len(self.word_dict.keys()) 
        total_tokens = sum(self.word_dict.values())
        print("BNC has %d unique terms, %d tokens" % (unique_terms, total_tokens))

if __name__ == "__main__":
    BNC = Process_BNC("/mnt/sdc3/home/BNC_XML/PlainTexts/", reprocess=False)
#    BNC.saveBNC("BNC.pickle")
    BNC.describe()
    BNC.CalcIDF()

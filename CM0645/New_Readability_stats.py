# -*- coding: utf-8 -*-

#from os import listdir
#from os.path import isfile, join
from pathlib import Path
import re
import sys
import collections
import pickle
import math

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#import textstat -- oroginal version
#from textstat.textstat import textstat

import textacy
import spacy
nlp = spacy.load('en')

import Settings as S                    # pathnames
from CM0645db import Db

basedir = S.basedir
dbfile = basedir / S.dbfile
outdir = basedir / S.cohortdir_16_17 / S.ptxts


#utility function from SO gives n sized chunks of list l
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

class Readability_Stats:
    data = ""
    debug = False # True False
    forced = False              # possibly override the efficiency option if data already in DB
    
    def __init__(self, mypath, Db, forced=False):
        p = Path(mypath)
        self.onlyfiles = sorted([f for f in p.iterdir() if f.is_file()])
        self.DB = Db
        self.forced = forced        #used to update db and sidestep time saving if values present
        with open(S.basedir / S.datadir / "myAWLDict.txt", "rb") as myFile:    #load Academic Word List
            self.AWLDictionary = pickle.load(myFile)
        with open(S.basedir / S.datadir / "myCSAWLDict.txt", "rb") as myFile2:
            self.CSAWL = pickle.load(myFile2)
        self.prepare_BNC()
 


#Read the filename 
#   
    def process_file(self, filename):
        with open(filename, 'r', encoding='utf8') as f:
            self.data = f.read()
        print("File: %s has %d lines" %(filename.name, len(self.data)))

#This takes self.content and extracts from the Abstract to the References to the outfile whilst
#         trying to lose none text lines like headers.
#
    def process_content(self, filenam):
        data = self.data        # file contents
        filename = filenam.name
        print("Text Stats; File:", filename)
        try:
            doc = textacy.Doc(data)
            pos_counts = collections.Counter(tok.pos_ for tok in doc)
            total  = sum(pos_counts.values())/100
            pos_proportions = {k:  v / total for k, v in pos_counts.items()}
            corpus_stats = self.Calculate_AWL(doc)
            ts = textacy.TextStats(doc)     #textacy returns an object with all this data
            self.DB.addTextStats(filename, {**ts.basic_counts, **ts.readability_stats, **pos_proportions, **corpus_stats})
            if self.debug:
                print("Filename: {}\n\tStats: {}".format(filename, ts.basic_counts))
        except (NameError, ValueError, UnboundLocalError, OSError) as e:
            print("File {} ERROR. caused '{}'".format(filename, e))

      
    def process_Dir(self):
        for file in self.onlyfiles:
            if self.forced or not self.DB.check_processed(file.name, 'n_sents'): # expensive op --don't repeat if done
                try:
                    self.process_file(file)
                    self.process_content(file)
                except Exception as e:
                    print("Readability Stats Error in {}, Reason {}".format(file, e))
        
    
    #prepare the BNC by loading the Pickle of raw frequences then 
#group into kilo-words. There are 822 of these.
    def prepare_BNC(self):
        BNCdict =  pickle.load(open( S.basedir / S.datadir / S.BNCfile, "rb" ))
        self.BNC = BNCdict
        #Sort by Frequency
        BNC_bv = sorted(BNCdict .items(), key=lambda kv: kv[1])
        #find 1000 word chunks
        self.kilo_words = list(chunks(BNC_bv, 1000))
        n_kilo_words = len(self.kilo_words)
        self.total_BNC_word = sum(BNCdict.values())
        self.LogTotval = math.log(self.total_BNC_word)
        #now create dicts of the kilo_word lists for quick look up
        self.kdicts = [dict(l) for l in reversed(self.kilo_words)]
        print("BNC: Total Word:", self.total_BNC_word, " # 1000 Word groups: ", n_kilo_words)
        if self.debug:
            self.BNC_info(self.total_BNC_word)

#Print frequency characteristics from the 
    def BNC_info(self, total_word_count):
        counter = 0
        cumulative = 0
        max_cumulative = 90
        for subl in reversed(self.kilo_words):
            cnt = sum([x[1] for x in subl])
            prop = (cnt*100.0)/total_word_count
            cumulative += prop
            print(counter, ") Raw(n): ", cnt, "Proportion(%): ", prop, " Cumulative(%): ", cumulative)
            counter +=1
            if cumulative > max_cumulative:   #otherwise get 823 lines of output
                break


           
    #Calculates AWL and BNC Membership
    def Calculate_AWL(self, doc):
        AWLtotal = 0
        CSAWLtotal = 0
        TotalIC = 0
        rmax = 0 
        dictback = {}
        novel_words = {}
        k1 = 0  #first thousand
        k2 = 0
        k3 = 0
        k4 = 0  #4th thousand BNC freq
        kn = 0  #otherwise in BNC
        kx = 0  #not in BNC at all
#        max_possible = sum(self.word_dict.values())

        for word, count in doc.to_bag_of_words(as_strings=True).items():
            rmax += count
            if word in self.BNC:
                if count == 1:
                    TotalIC += self.LogTotval/self.BNC[word]
                else:           # 1 + 1/2 + 1/3 ... 1/count Tailor series harmonic expansion
                    TotalIC += (math.log(count) + 0.577 +1/(2*count))* self.LogTotval/self.BNC[word] #  0.577 ~= Euler–Mascheroni constant 
                if word in self.kdicts[0]:
                    k1 += count
                elif word in self.kdicts[1]:
                    k2 += count
                elif word in self.kdicts[2]:
                    k3 += count
                elif word in self.kdicts[3]:
                    k4 += count
                else:
                    kn += count
            else:
                kx += count
                novel_words[word] = count
#CSAWL and AWL
            if word in self.AWLDictionary:
                AWLtotal += count
            if word in self.CSAWL:
                CSAWLtotal += count
        #normalize AWL CSAWL by document length
        AWLresult = AWLtotal
        dictback['AWL_count'] = AWLresult
        dictback['CSAWL_count'] = CSAWLtotal
        dictback['LFP_k1'] = k1/rmax   #in first 1000 BNC Words
        dictback['LFP_k2'] = k2/rmax   #in 2nd 1000 BNC Words
        dictback['LFP_k3'] = k3/rmax   #in 3rd 1000 BNC Words
        dictback['LFP_k4'] = k4/rmax   #in 4th 1000 BNC Words
        dictback['LFP_kn'] = kn/rmax   #not in first 4000 BNC Words, but in BNC
        dictback['LFP_kx'] = kx/rmax    #not in the BNC
        dictback['Rel_BNC'] = TotalIC   #Total information content of Doc
        if self.debug:
            print("AWL: %d/%d: %4.3f" %(AWLtotal, rmax, AWLresult))
            print("CSAWL: %d %d: " %(CSAWLtotal, rmax))
            print("LFP: k1:%4.3f, k2:%4.3f,  k3:%4.3f k4: %4.3f, kn: %4.3f, kx: %4.3f" %
            (k1*100/rmax, k2*100/rmax, k3*100/rmax, k4*100/rmax, kn*100/rmax, kx*100/rmax))
#        for key,val in self.novel_words.items():   # for debug
#            print("Novel:", key, "=>", val)
            print("Novel Words: {0} \n" . format(len(novel_words)))
        return(dictback)

        
    def Describe(self):
        print("Possible files: ", len(self.onlyfiles))
        

if __name__ == "__main__":
    DB = Db(basedir / S.dbfile)
    readability1 = Readability_Stats(outdir, DB)
    readability1.Describe()
    justone =  False    #True False
    if justone:
        file1 = readability1.onlyfiles[163]   #164 Rory broken
        readability1.process_file(file1)
        readability1.process_content(file1)
        readability1.Describe()
    else:
        Readability1 = Readability_Stats(basedir / S.cohortdir_15_16 / S.ptxts, DB, forced = True)   #tag the extracted texts
        Readability1.process_Dir()
        Readability2 = Readability_Stats(basedir / S.cohortdir_16_17 / S.ptxts, DB, forced = True)   #tag the extracted texts
        Readability2.process_Dir()
        Readability3 = Readability_Stats(basedir / S.cohortdir_17_18 / S.ptxts, DB, forced = True)   #tag the extracted texts
        Readability3.process_Dir()






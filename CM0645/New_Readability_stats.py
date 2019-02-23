# -*- coding: utf-8 -*-

from os import listdir
from os.path import isfile, join
import re
import sys

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

class Readability_Stats:
    mybase = ""
    data = ""
    
    def __init__(self, mypath, Db):
        onlyfiles = [f for f in sorted(listdir(mypath)) if isfile(join(mypath, f))]
        self.onlyfiles = onlyfiles
        self.DB = Db
        self.mybase = mypath

#Read the filename 
#   
    def process_file(self, filename):
        fname = self.mybase / filename
        with open(fname, 'r') as f:
            self.data = f.read()
        print("File: %s has %d lines" %(fname, len(self.data)))

#This takes self.content and extracts from the Abstract to the References to the outfile whilst
#         trying to lose none text lines like headers.
#
    def process_content(self, filename):
        data = self.data        # file contents
        print("Text Stats; File:", filename)
        try:
            doc = textacy.Doc(data)
            ts = textacy.TextStats(doc)     #textacy returns an object with all this data
            self.DB.addTextStats(filename, ts.basic_counts)
            self.DB.addTextStats(filename, ts.readability_stats)
        except (NameError, ValueError, UnboundLocalError, OSError) as e:
            print("File {} ERROR. caused '{}'".format(filename, e))


        
    def process_Dir(self):
        for file in self.onlyfiles:
            try:
                if not self.DB.check_processed(file, 'n_sents'): # expensive op --don't repeat if done
                    self.process_file(file)
                    self.process_content(file)
            except Exception as e:
                print("Text Stats Error in {}, Reason {}".format(file, e))
        
        
    def Describe(self):
        print("Possible files: ", len(self.onlyfiles))
        

if __name__ == "__main__":
    dbfile = S.dbfile
    DB = Db(basedir + dbfile)
    readability1 = Readability_Stats(outdir, DB)
    readability1.Describe()
    justone = False     #True
    if justone:
        file1 = readability1.onlyfiles[163]   #164 Rory broken
        readability1.process_file(file1)
        readability1.process_content(file1)
        readability1.Describe()
    else:
        Readability1 = Readability_Stats(basedir + S.cohortdir_15_16 + S.ptxts, DB)   #tag the extracted texts
        Readability1.process_Dir()
        # Readability2 = Readability_Stats(basedir + S.cohortdir_16_17 + S.ptxts)   #tag the extracted texts
        # Readability2.process_Dir()
        # Readability3 = Readability_Stats(basedir + S.cohortdir_17_18 + S.ptxts)   #tag the extracted texts
        # Readability3.process_Dir()






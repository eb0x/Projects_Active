import os
import re
import sys
import csv
import unittest
import importlib
import warnings
import pickle
import math
import sqlite3
import time
import pandas as pd
import numpy as np

from os import listdir
#from os.path import isfile, join # the old way to do paths
from pathlib import Path         # python 3 way
from sqlite3 import Error

# Projects Active Modules
#
#import test_CM0645_installation as test # Check installation has required packages  -- now imported into body
import Settings as S                    # pathnames
import Messages as m                    # enums and print related
import extract_parts_v2 as extract_m # re based text extractor
import Process_BNC as BNC_m     # BNC_m = BNC Module
import CM0645db as Db_m         # Db_m  = DB Module
import Data_Prep_v3 as DP_m     # DP_m = data prep module
import Token_Tag as Tag_m       # Tag_m = data prep module
import New_Readability_stats as Stats_m # Text Statistics module
import gui_01 as gui                    # gui Module


dbfile = S.basedir / S.dbfile
BNCfile = S.BNCfile


def libcheck(lib):
    '''lib is a library name as a string. If it is imported then a
    module object is returned. If not 0. A library will not be imported if
    not installed'''
    i = 0
    try:
        i = importlib.import_module(lib)
        print('Loaded: ', lib)
    except ImportError:
        print("The library: ", lib, " could not be loaded")
    return i

## This is a unittest class. Running this checks your installation
##
class CM0645Test(unittest.TestCase):

    def setUp(self):
        pass

    def test_DB_check(self):
        '''checks DB requirements'''
        warnings.simplefilter('ignore', category=ImportWarning)
        res = libcheck('os')
        res1 = libcheck('sqlite3')
        self.assertTrue(res)
        self.assertTrue(res1)

    def test_Data_Prep_check(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        res = libcheck('numpy')
        res2 = libcheck('operator')
        res3 = libcheck('matplotlib')
        res4 = libcheck('pandas')
        res5 = libcheck('re')
        self.assertTrue(res)
        self.assertTrue(res2)
        self.assertTrue(res3)
        self.assertTrue(res4)
        self.assertTrue(res5)


    def test_csawl_check(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        res = libcheck('nltk')
        res2 = libcheck('pickle')
        msg = ""
        try:
            from nltk.stem.snowball import SnowballStemmer
            msg = msg + "\nLoaded SnowballStemmer"
            print(msg)
        except:
            print(msg)
            print("The supporting data: could not be loaded")
        self.assertTrue(res)
        self.assertTrue(res2)

    def test_Token_Tag_check(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        res = 0
        msg = ""
        libcheck('pickle')
        libcheck('csv')
        libcheck('os')
        libcheck('spacy')
        libcheck('nltk')
        libcheck('nltk.data')
        libcheck('nltk.tokenize')
        libcheck('nltk.tag')
        libcheck('nltk.corpus')
        try:
            from nltk.stem.snowball import SnowballStemmer
            from nltk.tokenize import sent_tokenize,  word_tokenize, TreebankWordTokenizer
            tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
            nlp = spacy.load('en') # needed in Readablity
            msg = msg + "\nLoaded SnowballStemmer"
            msg = msg + "sent_tokenize,  word_tokenize, TreebankWordTokenizer"
            msg = msg + "\nLoaded tokenizers/punkt/english.pickle"
            print(msg)
        except:
            print(msg)
            print("--- Token tag data: could not be loaded -- Nothing will be processed")

#The purpose of the controller class is to link callable parts of the app so that
# it can be called from the gui. As far as possible leave callable elements in the modules

class Controller:
    DB = False
    cohorts = []
    gui = False
    output_level = m.Warnings.Verbose
    
    def __init__(self, dbfile):
        self.cohorts = []
        self.basedir = S.basedir
        self.DB = dbfile
        self.dbfile = dbfile


    #Methods to process BNC -- takes several hours
    # generally reload from pickle file rather than re-creating
    #http://www.natcorp.ox.ac.uk/corpus/index.xml?ID=numbers
    
    def processBNC(self):
        self.BNC = Process_BNC("/mnt/sdc3/home/BNC_XML/PlainTexts/")
        self.BNC.process_all()
        self.BNC.saveBNC(BNCfile)

    def describeBNC(self):
        self.BNC.describe()

        #Database section -- this is a sqlite db

    def getDB(self, dbfile):
        cohorts = []
        try:
            self.DB = Db_m.Db(dbfile)
            self.DB.index_filenames()
            cohorts = self.DB.FindLoadedCohortsRaw('raw')
            [self.addCohort(cohort) for cohort in cohorts]
        except:
            self.InitializeDB()
        self.DB.ShowTables()
        self.gprint("Loaded Cohort(s):{}".format(cohorts))
        self.gprint(cohorts)
        

    def InitializeDB(self):
        self.DB.initialize()

        ## Data Prep -- Loads Cohort
        ##
    def addCohort(self, label):
        unrecognised = False
        label = label.replace("/", "_")
        loaded = self.DB.FindLoadedCohortsRaw('raw') #cohort in DB
        for cohort in self.cohorts:     #might be a cohort obj already
            if label == cohort.label:
                return cohort
        self.gprint("addCohort: loaded {}, Label {}".format(loaded, label))
        if label == "15_16":
            marksfile = S.marksfile_15_16
            cohortdir = S.cohortdir_15_16 
        elif label == "16_17":
            marksfile = S.marksfile_16_17
            cohortdir = S.cohortdir_16_17
        elif label == "17_18":
            marksfile = S.marksfile_17_18
            cohortdir = S.cohortdir_17_18
        else:
            print("Cohort Label {} not recognised". format(label))
            unrecognised = True
        if not unrecognised:
            cohort = DP_m.Cohort(label, cohortdir, marksfile)
            self.cohorts.append(cohort)
            return cohort
        else:
            return False

        ##NLTK, AWL, LFP, Tagging

    def Extract_Parts(self):
        start = time.time()
        if not self.DB:
            self.getDB(dbfile)
        loaded_cohorts = self.DB.FindLoadedCohortsRaw('raw')
        for acohort in self.cohorts:
            if acohort.label not in loaded_cohorts:
                pt = extract_m.PlainText(acohort.txtdir, self.DB)
                pt.process_Dir(acohort.ptxtdir)
            else:
                self.gprint("Cohort {} already loaded" .format(acohort.label))
            self.gprint("Extract_Parts: Cohort {} processed from raw".format(acohort.label))
        end = time.time()
        self.gprint("Extract Parts  took {} seconds".format(end - start) )

    def GetData(self):
        start = time.time()
        if not self.DB:
            self.getDB(dbfile)
        cohorts = self.DB.FindLoadedCohortsRaw('raw')
        if self.cohorts == []:
            self.cohorts = [self.addCohort(cohort) for cohort in cohorts]
        [acohort.GetMarksData(self.DB) for acohort in self.cohorts if acohort]
        end = time.time()
        self.gprint("Get Raw Data  took {} seconds".format(end - start) )

        
    def TagCohort(self, cohort):
        tagger = Tag_m.TaggedText(cohort.ptxtdir, self.DB)
        tagger.process_Dir(cohort.taggeddir)

        #Tag loaded Cohort
    def TagCohorts(self):
        start = time.time()
        if not self.DB:
            self.getDB(dbfile)
        [self.TagCohort(acohort) for acohort in self.cohorts]
        end = time.time()
        self.gprint("Tag loaded Cohort took {} seconds".format(end - start) )

        ##Text Statistics: Fleisch Kincaid etc.
        ##
    def StatsCohort(self, cohort):
        Readability = Stats_m.Readability_Stats(cohort.ptxtdir, self.DB)
        Readability.process_Dir() #cohort.taggeddir

        #Stats of loaded Cohort
        #
    def StatsCohorts(self):
        start = time.time()
        if not self.DB:
            self.getDB(dbfile)
        [self.StatsCohort(acohort) for acohort in self.cohorts]
        end = time.time()
        self.gprint("Text Statistics took {} seconds".format(end - start) )

        
    def setGui(self, gui):
        self.gui = gui

    def gprint(self, text, level=False):
        if not level:
            level = self.output_level
#        print("gprint output level {}".format(level))
        if self.gui:
            self.gui.gprint(text, level)
        else:
            print(text)
#        oldtext = self.gui.GetValue()
#        newtext = oldtext + "\n" + text
#        self.gui.SetValue(text)

#Code in this block is executed when this file is loaded as the main file
# but not when the module is imported



if __name__ == "__main__":
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=ImportWarning)
            unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True: # raised by sys.exit(True) when tests failed
            raise
        
    dbfile = str(S.dbfile)
    cntrl = Controller(dbfile)
    cntrl.getDB(dbfile)
    gui.main(cntrl)

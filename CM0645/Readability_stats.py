# -*- coding: utf-8 -*-

from os import listdir
from os.path import isfile, join
import re
import sys

#import textstat
from textstat.textstat import textstat
from CM0645db import Db


#if changing the folders, please comment out these lines and add your own
# it is easier then to swap hosts
basedir = "/Users/jeremyellman/Documents/Projects_Active/CM0645_15_16/"
basedir = "/home/izje1/Documents/Projects_Active/"
outdir = basedir + 'CM0645_15_16/ptxts/'

class Readability_Stats:
    mybase = ""
    data = ""
    
    def __init__(self, mypath):
        self.onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        self.mybase = mypath

#Read the filename 
#   
    def process_file(self, filename):
        fname = self.mybase  + filename
        with open(fname) as f:
            self.data = f.read()
#        print("File: %s has %d lines" %(fname, len(self.content)))

#This takes self.content and extracts from the Abstract to the References to the outfile whilst
#         trying to lose none text lines like headers.
#
    def process_content(self, filename):
        data = self.data
        print("File:", filename)

        print("Syl", textstat.syllable_count(data))
        ourTSdict = {\
        'ts_char_count' : textstat.char_count(data),\
        'ts_lexicon_count' : textstat.lexicon_count(data),\
        'ts_syllable_count' : textstat.syllable_count(data),\
        'ts_sentence_count' : textstat.sentence_count(data),\
        'ts_avg_sentence_length' : textstat.avg_sentence_length(data),\
        'ts_avg_syllables_per_word' : textstat.avg_syllables_per_word(data),\
        'ts_avg_letter_per_word' : textstat.avg_letter_per_word(data),\
        'ts_avg_sentence_per_word' : textstat.avg_sentence_per_word(data),\
        'ts_flesch_reading_ease' : textstat.flesch_reading_ease(data),\
        'ts_flesch_kincaid_grade' : textstat.flesch_kincaid_grade(data),\
        'ts_polysyllabcount' : textstat.polysyllabcount(data),\
        'ts_smog_index' : textstat.smog_index(data),\
        'ts_coleman_liau_index' : textstat.coleman_liau_index(data),\
        'ts_automated_readability_index' : textstat.automated_readability_index(data),\
        'ts_linsear_write_formula' : textstat.linsear_write_formula(data),\
        'ts_difficult_words' : textstat.difficult_words(data),\
        'ts_dale_chall_readability_score' : textstat.dale_chall_readability_score(data),\
        'ts_gunning_fog' : textstat.gunning_fog(data),\
 #       'ts_lix' : textstat.lix(data),\
 #       'ts_text_standard' : textstat.text_standard(data)
        }
        print("Results:" , ourTSdict)
        # cols = [key + "=?," for key in ourTSdict.keys() ]
        # vals = ', '.join(map(str,ourTSdict.values()))
        # vals2 = '(' + vals + ' "' + filename + '")'
        # sql = 'UPDATE projects SET ' + ' '.join(map(str, cols))
        # print("SQL:", sql[:-1] + ' WHERE filename=?')
        # print("VALS", vals2)
        DB.addTextStats(filename, ourTSdict)


    def process_Dir(self):
        for file in self.onlyfiles:
            try:
                self.process_file(file)
                self.process_content(file)
            except Exception as e:
                        print(e)
        

    def Describe(self):
        print(self.onlyfiles)
        
if __name__ == "__main__":
    dbfile = 'CM0645.sqlite'
    DB = Db(basedir + dbfile)
    DB.index_filenames()
    basedir += "CM0645/"
    JustOne = False #True #
    if JustOne:
        Readability0 = Readability_Stats(basedir + 'CM0645_Projects_15_16/' + 'ptxts/')   #tag the extracted texts
        file1 = Readability0.onlyfiles[12]
        Readability0.process_file(file1)
        Readability0.process_content(file1, outdir + file1)
    else:
        Readability1 = Readability_Stats(basedir + 'CM0645_Projects_15_16/' + 'ptxts/')   #tag the extracted texts
        Readability1.process_Dir()
        Readability2 = Readability_Stats(basedir + 'CM0645_Projects_16_17/' + 'ptxts/')   #tag the extracted texts
        Readability2.process_Dir()
        Readability3 = Readability_Stats(basedir + 'CM0645_Projects_17_18/' + 'ptxts/')   #tag the extracted texts
        Readability3.process_Dir()





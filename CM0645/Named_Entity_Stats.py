from pathlib import Path

from collections import Counter
import textacy
import spacy
# Using model from: https://spacy.io/models/en#en_core_web_md
nlp = spacy.load('en_core_web_md')

import Settings as S # Path Names
from CM0645db import Db

basedir = S.basedir
dbfile = basedir / S.dbfile
outdir = basedir / S.cohortdir_16_17 / S.ptxts

class Named_Entity_Stats:
    data = ""
    debug = True

    def __init__(self, mypath, Db):
        p = Path(mypath)
        self.onlyfiles = sorted([f for f in p.iterdir() if f.is_file()])
        self.DB = Db

    def process_file(self, filename):
        with open(filename, 'r', encoding='utf8') as f:
            self.data = f.read()
        print("File: %s has %d lines" %(filename.name, len(self.data)))

# This takes self.content and extracts from the Abstract to the References to the outfile whilst
# trying to lose none text lines like headers.

    def process_content(self, filenam):
        data = self.data        # file contents
        filename = filenam.name
        print("Text Stats; File:", filename)
        try:
            # Extend Maximum Character Size according to file content plus 10k contingency
            nlp.max_length = len(data) + 10000
            # Using Spacy to extract Named Entities
            doc = nlp(data)
            # Create a Dictionary of Named Entity Labels and Count
            dict = Counter()
            for entity in doc.ents:
                dict['ent_' + entity.label_.lower()] += 1
            # Add Statistics to DB File
            self.DB.addTextStats(filename, dict)

            if self.debug:
                print("Filename: {}\n\tStats: {}".format(filename, dict))
        except (NameError, ValueError, UnboundLocalError, OSError) as e:
            print("File {} ERROR. caused '{}'".format(filename, e))

    # Print The Text and Label of Each Named Entity in Document
    def print_named_Entities(self, doc_file):
        for ent in doc_file.ents:
            print(ent.text, ent.label_)

    # Print The Count of Each Named Entity Label in Document
    def print_named_Entity_Counts(self, doc_file):
        labels = [x.label_ for x in doc_file.ents]
        counter = Counter(labels)
        print(counter)

    def process_Dir(self):
        for file in self.onlyfiles:
            if not self.DB.check_processed(file.name, 'ent_person'):  # expensive op --don't repeat if done
                try:
                    self.process_file(file)
                    self.process_content(file)
                except Exception as e:
                    print("Named Entities Stats Error in {}, Reason {}".format(file, e))

    def Describe(self):
        print("Possible files: ", len(self.onlyfiles))

if __name__ == "__main__":
    DB = Db(basedir / S.dbfile)
    namedEntity = Named_Entity_Stats(outdir, DB)
    namedEntity.Describe()

    justone =  False    #True False
    if justone:
        file1 = namedEntity.onlyfiles[103]   #164 Rory broken
        namedEntity.process_file(file1)
        namedEntity.process_content(file1)
        namedEntity.Describe()
    else:
        NamedEntity1 = Named_Entity_Stats(basedir / S.cohortdir_15_16 / S.ptxts, DB)   #tag the extracted texts
        NamedEntity1.process_Dir()
        NamedEntity2 = Named_Entity_Stats(basedir / S.cohortdir_16_17 / S.ptxts, DB)   #tag the extracted texts
        NamedEntity2.process_Dir()
        NamedEntity3 = Named_Entity_Stats(basedir / S.cohortdir_17_18 / S.ptxts, DB)   #tag the extracted texts
        NamedEntity3.process_Dir()

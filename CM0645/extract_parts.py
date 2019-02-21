# -*- coding: utf-8 -*-

from os import listdir
from os.path import isfile, join
import re
import sys
import time

from CM0645db import Db

#if changing the folders, please comment out these lines and add your own
# it is easier then to swap hosts
#only last one counts
basedir = "/Users/jeremyellman/Documents/Projects_Active/CM0645_15_16/"
basedir = "/home/izje1/Documents/Projects_Active/CM0645/"
#basedir = "/home/jeremy/Projects-Active/CM0645/CM0645_Projects_15_16/"

outdir = basedir + 'ptxts/'

#Given a filename from eLP get firstname/surname using their structure convention
#
def extract_student_name(filename):
    name_end = filename.rfind("-")
    wholename = filename[0:name_end]
    firstname_ends = wholename.find("_")
    firstname = wholename[0:  firstname_ends ]
    surname = wholename[ firstname_ends + 1:]
    find_again = surname.find("-")
    if (find_again > 0): 
        surname = surname[0: find_again]
 #       print("Firstname: {:s}, Surname: {:s}" .format(firstname, surname))
    return (firstname, surname)


class PlainText:
    mybasedir = ""
    debug = False
    
    def __init__(self, mypath, db):
        self.onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        self.mybasedir = mypath
        self.DB = db
        

#Read the filename content into one variable self.content
#   
    def process_file(self, filename):
        fname = self.mybasedir  + filename
        with open(fname, 'r') as f:
            self.content = f.readlines()
        if self.debug: 
            print("File: %s has %d lines" %(fname, len(self.content)))

#This takes self.content and extracts from the Abstract to the References to the outfile whilst
#         trying to lose none text lines like headers.
#
    def process_content(self, outfilename):
        with open(outfilename, 'w') as the_file:
            found_abstract = False
            line_count = 0
            lines_written = 0 
            for line in self.content:
                #line = line.rstrip()
                line_count += 1
                if found_abstract:
                    if re.search(r'[\d\.\)\s]*(References|Bibliography|Reference List)\:*$', line.strip(), re.IGNORECASE) and line_count > 400:
                        found_references = True #Not interested in text after here
                        if self.debug: 
                            print("---%s---" %(line.strip()))
                        break
                    line = line.replace('\t', ' ') 
                    line = line.replace(r'\s+', ' ')    
                    line = re.sub(r'[^\x00-\x7f|\x0C]',r'', line)
                    line = line.replace(r'_', '') #replace form feeds?
                    line = line.replace('\x0C', '')
                    index_line_p = re.search(r'\W+\d\d?\s*$', line.rstrip()) # ToC line
    
                    if not index_line_p:
                        blankline = re.match('^\s*[\d\.]+\s*$', line)  # page numbering
                        if not blankline:
                            if not line in ['\n', '\r\n']:
                                the_file.write(line + ' ')
                                lines_written += 1
        #            else:
        #                print("Index >>%s<<" % (line))
                else:
                    if re.search(r'^[\d\.\)\s]*(Acknowledgements|Abstract|Introduction|Chapter 1)\:*\.?$', line.strip(), re.IGNORECASE): # and not re.search(r'[ \.]?\d+', line.rstrip()):
                        if self.debug: 
                            print("+++%s+++" %(line.strip()))
                        found_abstract = True;
                        the_file.write(line + ' ')
                        lines_written += 1
            if self.debug: 
                print("Lines read %d, written %d" %(line_count, lines_written ))
            return (line_count, lines_written )

    def process_Dir(self, outdir):
        files_data = []
        for afile in self.onlyfiles:
            cohort = ""
            try:
                (firstname, surname) = extract_student_name(afile) #--10/1/
                group = re.search(r'_(\d\d_\d\d)', outdir, re.M|re.I)
                if group: 
                    cohort  = group.group(1)
                self.process_file(afile)
                (line_count, lines_written ) = self.process_content(outdir + afile)
                #self.DB.add_file(afile,  firstname, surname, cohort,  line_count, lines_written )
                files_data.append([afile,  firstname, surname, cohort,  line_count, lines_written ])
            except Exception as e:
                        print("Extract parts: Process Error in {}, reason: {}".format(afile, e))
        print("Length File Data {}".format(len(files_data)))
        self.DB.add_files(files_data)


    

    
    def Describe(self):
        print(self.onlyfiles)
        
if __name__ == "__main__":
#  basedir = "/home/jeremy/Projects-Active/CM0645/"
    start = time.time()
    basedir = "/home/izje1/Documents/Projects_Active/"
    dbfile = 'CM0645.sqlite'
    DB = Db(basedir + dbfile)
    DB.initialize() # reset DB
    pt1 = PlainText(basedir + 'CM0645_Projects_15_16/' + 'txts/', DB)
    pt1.process_Dir(basedir + 'CM0645_Projects_15_16/' + 'ptxts/')
    pt2 = PlainText(basedir + 'CM0645_Projects_16_17/' + 'txts/', DB)
    pt2.process_Dir(basedir + 'CM0645_Projects_16_17/' + 'ptxts/')
    pt3 = PlainText(basedir + 'CM0645_Projects_17_18/' + 'txts/', DB)
    pt3.process_Dir(basedir + 'CM0645_Projects_17_18/' + 'ptxts/')
    end = time.time()
    print("Loading took {} seconds".format(end - start) )
 #   





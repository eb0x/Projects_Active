#from os import listdir
#from os.path import isfile, join # old
from pathlib import Path
import re
import sys
import time
import textacy

import Settings as S                    # pathnames
import CM0645db as Db_m         # Db_m  = DB Module

basedir = S.basedir
outdir = basedir /  S.ptxts

#Given a filename from eLP get firstname/surname using their structure convention
#
def extract_student_name(filenam):
    filename = filenam.stem
    name_end = filename.rfind("-")
    wholename = filename[0:name_end]
    firstname_ends = wholename.find("_")
    firstname = wholename[0:  firstname_ends ]
    surname = wholename[ firstname_ends + 1:]
    find_again = surname.find("-")
    if (find_again > 0): 
        surname = surname[0: find_again]
        print("Firstname: {:s}, Surname: {:s}" .format(firstname, surname))
    return (firstname, surname)
	

class PlainText:
    mybasedir = ""
    debug = False # False True
    
    def __init__(self, mypath, db):
        p = Path(mypath)
#        self.onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        self.onlyfiles = [f for f in p.iterdir() if f.is_file()]
        self.mybasedir = mypath
        self.DB = db
        

#Read the filename content into one variable self.content
#   
    def process_file(self, filename):
        fname = self.mybasedir  / filename
		# Choose utf8 encoding when opening file to ignore non-utf-8 characters
        with open(fname, 'r', encoding="utf8") as f:
            self.content = f.readlines()
        if self.debug: 
            print("File: %s has %d lines" %(fname, len(self.content)))
            
#This takes self.content and extracts from the Abstract to the References to the outfile whilst
#         trying to lose none text lines like headers.
#
    def process_content(self, outfilename):
        with open(outfilename, 'w', encoding='utf8') as the_file:
            found_abstract = False
            found_TOC = False
            line_count = 0
            lines_written = 0 
            for line in self.content:
                # Clean Text to remove/ replace bad_unicode chars, urls, emails, phone nos, and accented character
                # Boolean for options: fix_unicode, lowercase, no_urls, no_emails, no_phone_numbers, no_numbers, no_currency_symbols, no_punct, no_contractions, no_accents
                # https://chartbeat-labs.github.io/textacy/api_reference.html#module-textacy.preprocess
                line = textacy.preprocess_text(line, True, False, True, True, True, False, False, False, False, True)
                line_count += 1
                if found_TOC:
                    # Find Table of Contents
                    if re.search(r'[\d\.\)\s]*(Table of Content|Content|List of Content|TOC|Appendix)\:*$', line.strip(), re.IGNORECASE):
                        found_TOC = True
                        if self.debug: 
                            print("---%s---" %(line.strip()))
                        break
                        # Remove Table of Contents
                        re.sub(r"[\d\.\)\s]*(...)",r'', line)
                        
                if found_abstract:
                    if re.search(r'[\d\.\)\s]*(References|Bibliography|Reference List)\:*$', line.strip(), re.IGNORECASE) and line_count > 400:
 #                       found_references = True #Not interested in text after here
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
                        blankline = re.match(r'^\s*[\d\.]+\s*$', line)  # page numbering
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
                        found_abstract = True
                        # Remove spaces and non-utf8 characters in 'Absract' line, add a new line after Abstract
                        the_file.write(line.strip() + '\n ')
                        
                        lines_written += 1
            if self.debug: 
                print("Lines read %d, written %d" %(line_count, lines_written ))
            return (line_count, lines_written )

    def process_Dir(self, outdir):
        files_data = []
        for afile in self.onlyfiles:
       #     afile = str(afile_p)
            cohort = ""
            try:
                (firstname, surname) = extract_student_name(afile) #--10/1/
                group = re.search(r'_(\d\d_\d\d)', str(outdir), re.M|re.I)
                if group: 
                    cohort  = group.group(1)
                self.process_file(afile)
                (line_count, lines_written ) = self.process_content(outdir / afile.name)
                #self.DB.add_file(afile,  firstname, surname, cohort,  line_count, lines_written )
                files_data.append([afile.name,  firstname, surname, cohort,  line_count, lines_written ])
            except Exception as e:
                        print("Extract parts: Process Error in {}, reason: {}".format(afile.name, e))
        print("Length File Data {}".format(len(files_data)))
        self.DB.add_files(files_data)

    def Describe(self):
        print(self.onlyfiles)

if __name__ == "__main__":
    start = time.time()
    basedir = S.basedir
    dbfile = S.dbfile
    DB = Db_m.Db(basedir / dbfile)
    DB.initialize() # reset DB
    pt1 = PlainText(basedir / S.cohortdir_15_16 / S.txts, DB)
    pt1.process_Dir(basedir / S.cohortdir_15_16 / S.ptxts)
    pt2 = PlainText(basedir / S.cohortdir_16_17 / S.txts, DB)
    pt2.process_Dir(basedir / S.cohortdir_16_17 / S.ptxts)
    pt3 = PlainText(basedir / S.cohortdir_17_18 / S.txts, DB)
    pt3.process_Dir(basedir / S.cohortdir_17_18 / S.ptxts)
    end = time.time()
    print("Loading took {} seconds".format(end - start) )

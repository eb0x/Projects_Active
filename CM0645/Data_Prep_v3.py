from os import listdir
#from os.path import isfile, join
from pathlib import Path         # python 3 way
import pandas as pd
import numpy as np
import math
import re

import Settings as S                    # pathnames
from CM0645db import Db
import extract_parts_v2 as extract_m # re based text extractor

#The main point of this class is to reconcile the files from the eLP (if any)
#with the marks and store an entry in the DB if both found

class Cohort:

    def __init__(self, label, cohortdir, marksfile ):
        self.marksfile = S.basedir / cohortdir / marksfile      #the file holding csv marks
        self.label = label                 #the label of this cohort eg '15-16'
        self.txtdir = S.basedir / cohortdir / S.txts               # the source text file
        self.ptxtdir = S.basedir / cohortdir / S.ptxts               # the processed text directory
        self.taggeddir = S.basedir / cohortdir / S.taggedtxts    # the tagged text directory

#Get the CSV marks spreadsheet as a pandas dataframe
#
    def get_marks(self):
        self.marks = pd.read_csv( self.marksfile)

#Get the file names into a dictionary indexed by surname
# filenames from eLP separate student names with '_' and titles with '-'
#need to later equate these to marks
#
    def get_files(self):
        p = Path(self.txtdir)
        onlyfiles = sorted([f for f in p.iterdir() if f.is_file()])
        file_details = dict()
        for file in onlyfiles:
            (firstname, surname) = extract_m.extract_student_name(file) 
            if surname in file_details:          # **HANDLE THIS BETTER! Will lose when surnames duplicates***
                print("Surname duplicated", surname)
            else:
                file_details[surname.upper()] = (surname, firstname, file) #store in dictionary 
        self.file_details = file_details

# Check that for all the marks, we have a file
#
    def equate_names_marks(self, db):
        uids_data = []
        find_count = 0
        for row_index,row in self.marks.iterrows():
            (surname, firstnames, markstr, maxMark) = self.get_NameMark(row)
            mark = 0            #default
            if surname not in self.file_details:
                searchObj = re.search( r'(\w+)([ -]).*', surname, re.M|re.I)
                if searchObj:
                    surname = searchObj.group(1)
                else:
                    if  not math.isnan(row['Report_Mark']):    #so there's a mark but no report
                        print("No Report Found: Cohort {}, Lastname: {}, Firstname: {}". format(self.label, surname, firstnames))
            firstnames = firstnames.strip()                     #lose leading/trailing
            if  isinstance(surname, str) and surname in self.file_details:
                (_, _, filename) = self.file_details[surname]
                if math.isnan(row['Report_Mark']) or math.isnan(row['Report_Max']):       #!No mark recorded
                    print("Report Mark Missing: Cohort {}, Lastname: {}, Firstname: {}". format(self.label, surname, firstnames))
                else:
                    uid  = self.get_UID(row)
                   # add_uid(self, uid, first_name, last_name, cohort, filename, Report_Mark, Report_Max):
                    if uid:
                        #db.add_uid(uid, firstnames, surname, self.label, filename, row['Report_Mark'], row['Report_Max'])
                        Report_Percent = (row['Report_Mark'] * 100.0) /row['Report_Max']
                        uids_data.append([uid, firstnames, surname, self.label, filename.name, row['Report_Mark'], row['Report_Max'],Report_Percent ])
                    find_count += 1
            else:
                pass
#                print("Missed file: %s_%s" % (firstnames, surname)) # duplicate msg
        db.add_uids(uids_data)
        print("Cases Found:", find_count)

#IDs look like w14040191, or 12015105/1
    def get_UID(self, row):
        uid = 0
        if 'ID' in row and row['ID']:
            ids = row['ID']
 #           print("Row: {%s}", row['ID'] )
            if isinstance(ids, float) or isinstance(ids, int):
                uid = int(ids)
            elif isinstance(ids, str):
                m = re.search(r'\d{8}', row['ID'])
                if m:
                    uid = int(m.group(0))
        return uid


#cope with some spreadsheets having the name in one column, others labelled 
    def get_NameMark(self, row):
        surname = firstnames =  markstr = maxMark = ""
        try:
            markstr = row['Report_Mark']
            maxMark = row['Report_Max']
            if 'Name' in row and isinstance(row['Name'], str):
                (surname, firstnames) = row['Name'].split(',')
            elif 'Last_Name' in row and 'First_Name' in row:
                firstnames = row['First_Name']
                surname    = row['Last_Name']
            else:
                print("get_NameMark: Bad Row", row)
        except:
            print("Bad Row: ", row)
        return (surname.upper(), firstnames.upper(),  markstr, maxMark)

#get the marks into the DB  from the CSV
#
    def GetMarksData(self, DB):
        print("GetMarksData: Get Marks", self.label)
        self.get_marks()
        self.get_files()
        self.equate_names_marks(DB)
    
    def describe(self, text):
        self.description = text
    
    def show(self):
        print("Cohort Label: ", self.label, " Marksfile: ", self.marksfile, " Text Dir:", self.txtdir)

# Execute this block  Main Module (standard trick) but not if included as module
# pay particular attention to the spreadsheet column headers
if __name__ == '__main__':
    dbfile = S.basedir / S.dbfile
    DB = Db(dbfile)
    #    DB.initialize()
    cohort_15_16 = Cohort("15-16", S.cohortdir_15_16, S.marksfile_15_16)
    cohort_15_16.describe(" Container of file details and marks")
    cohort_15_16.get_marks()
    cohort_15_16.get_files()
    cohort_15_16.equate_names_marks(DB)
    cohort_16_17 = Cohort("16-17", S.cohortdir_16_17, S.marksfile_16_17)
    cohort_16_17.describe(" Container of file details and marks")
    cohort_16_17.get_marks()
    cohort_16_17.get_files()
    cohort_16_17.equate_names_marks(DB)
    cohort_17_18 = Cohort("17-18", S.cohortdir_17_18, S.marksfile_17_18)
    cohort_17_18.describe(" Container of file details and marks")
    cohort_17_18.get_marks()
    cohort_17_18.get_files()
    cohort_17_18.equate_names_marks(DB)
    DB.index_filenames()
    DB.db_close()





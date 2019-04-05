from pathlib import Path  # python 3 way
import pandas as pd
import numpy as np
import math
import re

import Settings as S  # pathnames
from CM0645db import Db

basedir = S.basedir
dbfile = basedir / S.dbfile


class TAACO:
    def __init__(self, Db, resultfile):
        # TAACO results.csv in TAACO/results/ directory under the cohorts folder
        self.taacofile = S.basedir / resultfile  # TAACO results csv file
        self.DB = Db
        self.loadResultFile();

    # Load the TAACO csv as Pandas DataFrame
    def loadResultFile(self):
        try:
            self.taacoresult = pd.read_csv(self.taacofile)
        except Exception as e:
            print("Reading TAACO csv: Error in {}, reason: {}".format(self.taacofile.name, e))

    def processResults(self):
        try:
            # TAACO features in Pandas DF loaded from CSV
            taacodata = self.taacoresult
            # Project Data in Pandas from Database
            projectdata = self.DB.getDF("projects");

            # Retain only original projects table columns 1-68 [Filename, Scores, Textacy Features, etc]
            only_projects = projectdata.iloc[:, 0:68]
            # Merge original data in db with Pandas of TAACO results: Key Filename
            project_and_taaco = pd.merge(only_projects, taacodata, on='Filename', how='left')

            # Optional: Export the full current structure of the projects table to file
            # project_and_taaco.to_csv('export.csv', index=False)

            # Replace existing projects table with newly merged records
            # Notice: TAACO results must be full for all cohorts and records in the datasbase, if not,
            # the records without a TAACO result will be lost due to the replace
            project_and_taaco.to_sql('projects', DB.conn, if_exists='replace', index=False)

        except Exception as e:
            print("Processing TAACO csv to DB: Error in {}".format(e))

if __name__ == "__main__":
    # SQLite Database File
    DB = Db(basedir / S.dbfile)
    taaco = TAACO(DB, basedir / S.cohortdir_15_16 / S.taacoresultfile)
    taaco.processResults();

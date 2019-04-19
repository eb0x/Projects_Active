#from os import listdir
import sys
import sqlite3
from sqlite3 import Error
import csv
import pandas as pd

import Settings as S

#table_name = 'projects'

#Many Operations will be expensive, so store any values in the DB to avoid re-computing
#the idea is that the vectors input to the deep learning system will be extracted from 
#the db rows
# this is a key value store rather than a relational db

#Expect this to get lengthy
# Comment each feature FTW and NB SQL Comment Sysntax

raw = '''CREATE TABLE IF NOT EXISTS raw (
filename TEXT PRIMARY KEY,  
first_name TEXT NOT NULL,              
last_name TEXT NOT NULL,
cohort TEXT NOT NULL,
raw_lines integer default 0,
extracted_lines integer default 0
);'''

create = '''CREATE TABLE IF NOT EXISTS projects (
uid integer PRIMARY KEY,               -- UNN userID
first_name TEXT NOT NULL,              
last_name TEXT NOT NULL,
cohort TEXT NOT NULL,
filename TEXT NOT NULL,                -- full path to file txt
Report_Mark  REAL default 0,           -- the actual project mark as normalised percent
Report_Max INTEGER default 0,
Report_Percent REAL default 0,
AWL_count REAL default 0,       -- proportion of vocab from AWL
CSAWL_count REAL default 0,     -- proportion of vocab from CSAWL
LFP_k1 REAL default 0,          --1st 1000 BNC Words
LFP_k2 REAL default 0,          --2nd 1000 BNC Words
LFP_k3 REAL default 0,
LFP_k4 REAL default 0,
LFP_kn REAL default 0,          --in  BNC Words but not 4000
LFP_kx REAL default 0,          -- not in BNC
n_sents  INTEGER default 0,    --textacy textstats
n_words INTEGER default 0,
n_chars INTEGER default 0,
n_syllables INTEGER default 0,
n_unique_words INTEGER default 0,
n_long_words INTEGER default 0,
n_monosyllable_words INTEGER default 0,
n_polysyllable_words INTEGER default 0,
-- ts_avg_sentence_length REAL default 0, --derived text stats
-- ts_avg_syllables_per_word REAL default 0,
-- ts_avg_letter_per_word REAL default 0,
-- ts_avg_sentence_per_word REAL default 0,
flesch_kincaid_grade_level  REAL default 0, -- Textacy readability stats
flesch_reading_ease  REAL default 0,
smog_index  REAL default 0,
gunning_fog_index  REAL default 0,
coleman_liau_index  REAL default 0,
automated_readability_index  REAL default 0,
lix  REAL default 0,
gulpease_index  REAL default 0,
wiener_sachtextformel  REAL default 0,
-- ts_text_standard INTEGER default 0,
-- Heap_k REAL default 0,
Rel_BNC default 0,
ADJ  REAL default 0,            --Universal Tagset as in Textacy
ADP  REAL default 0,
ADV  REAL default 0,
CCONJ  REAL default 0,
DET  REAL default 0,
INTJ  REAL default 0,
NOUN  REAL default 0,
NUM  REAL default 0,
PART  REAL default 0,
PRON  REAL default 0,
PROPN  REAL default 0,
PUNCT  REAL default 0,
SPACE  REAL default 0,
SYM  REAL default 0,
VERB  REAL default 0,
X  REAL default 0,
ent_person REAL default 0, -- People, including fictional.
ent_norp REAL default 0, -- Nationalities or religious or political groups.
ent_fac REAL default 0, -- Buildings, airports, highways, bridges, etc.
ent_org REAL default 0, -- Companies, agencies, institutions, etc.
ent_gpe REAL default 0, -- Countries, cities, states.
ent_loc REAL default 0, -- Non-GPE locations, mountain ranges, bodies of water.
ent_product REAL default 0, -- Objects, vehicles, foods, etc. (Not services.)
ent_event REAL default 0, -- Named hurricanes, battles, wars, sports events, etc.
ent_work_of_art REAL default 0, -- Titles of books, songs, etc.
ent_law REAL default 0, -- Named documents made into laws.
ent_language REAL default 0, -- Any named language.
ent_date REAL default 0, -- Absolute or relative dates or periods.
ent_time REAL default 0, -- Times smaller than a day.
ent_percent REAL default 0, -- Percentage, including "%".
ent_money REAL default 0, -- Monetary values, including unit.
ent_quantity REAL default 0, -- Measurements, as of weight or distance.
ent_ordinal REAL default 0, -- "first", "second", etc.
ent_cardinal REAL default 0 -- Numerals that do not fall under another type.
);'''


class Db:
    """Wrapper Class for the SQLite Database"""
 #   table_name = 'projects'
    csv_name = "projects_derived"
    df = None                   # pandas dataframe from DB
    
    def __init__(self, db_file):
        try:
            conn = sqlite3.connect(str(db_file))
            print('SQLite Version OK', sqlite3.version)
            self.conn = conn
        except Error as e:
            print("DB file", db_file, ": ", e)

    def initialize(self):
        """(Re) Initialize the projects table"""
        drop = "DROP TABLE IF EXISTS projects;"
        drop2 = "DROP TABLE IF EXISTS raw;"
        try:
            self.conn.execute(drop)
            self.conn.execute(drop2)
            self.conn.commit()
            self.conn.execute(create)
            self.conn.execute(raw)
            self.conn.commit()
        except Error as e:
            print(e)

    def add_uid(self, uid, first_name, last_name, cohort, filename, Report_Mark, Report_Max):
        try:
            Report_Percent = (Report_Mark * 100.0) /Report_Max
            cursor = self.conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO projects(uid, first_name, last_name, cohort, filename, Report_Mark, Report_Max, Report_Percent)
                  VALUES(?,?,?,?,?,?,?,?)''', (uid, first_name, last_name, cohort, filename, Report_Mark, Report_Max, Report_Percent))
            self.conn.commit()
        except sqlite3.Error as e:
            self.logerror("Database error: %s" % e)
        except Exception as e:
            self.logerror("Exception in _query: %s" % e)
        return True

#Batched version of above
#
    def add_uids(self, uids_data):
        try:
            cursor = self.conn.cursor()
#            cursor.execute("BEGIN TRANSACTION;")
            sql = '''INSERT OR REPLACE INTO projects(uid, first_name, last_name, cohort, filename, Report_Mark, Report_Max, Report_Percent)
                  VALUES(?,?,?,?,?,?,?,?)'''
            cursor.executemany(sql, uids_data)
            cursor.execute("COMMIT;")
        except sqlite3.Error as e:
            self.logerror("Database error: %s" % e)
        except Exception as e:
            self.logerror("Exception in _query: %s" % e)
        return True

#record file data
    def add_file(self, filename, first_name, last_name, cohort,  raw_lines, extracted_lines):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO raw(filename, first_name, last_name, cohort,  raw_lines, extracted_lines)
                  VALUES(?,?,?,?,?,?)''', (filename, first_name, last_name, cohort,  raw_lines, extracted_lines))
            self.conn.commit()
        except sqlite3.Error as e:
            self.logerror("Database error: %s" % e)
        except Exception as e:
            self.logerror("Exception in _query: %s" % e)
        return True

#multi-file version of above
#
    def add_files(self, files_data):
        try:
            cursor = self.conn.cursor()
#            cursor.execute("BEGIN TRANSACTION;")
            sql = '''INSERT OR REPLACE INTO raw(filename, first_name, last_name, cohort,  raw_lines, extracted_lines) VALUES(?,?,?,?,?,?)'''
            cursor.executemany(sql, files_data)
            cursor.execute("COMMIT;")
          #  self.conn.commit()
        except sqlite3.Error as e:
            self.logerror("Database error: %s" % e)
        except Exception as e:
            self.logerror("Exception in _query: %s" % e)
        return True

#Pass the statistics in a dict, so the number of stats can vary
#
    def addTextStats(self, filename, TS_dict):
#        print("TS_dict", TS_dict)
        cols = [key + "=" + str(value) + "," for (key, value) in TS_dict.items()]
        sql = 'UPDATE projects SET ' + ' '.join(map(str, cols))
        sql2 = sql[:-1] + ' WHERE filename=?'
        print("addTextStats::Query: ", sql2)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql2, (filename,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.logerror("Database error: %s" % e)
        except Exception as e:
            self.logerror("Exception in _query: %s" % e)
        return True

    # to avoid reprocessing data in db. If recalc is really needed, zero db.
    #
    def check_processed(self, filename, column):
        sql = '''SELECT {} from projects where filename=?;'''.format(column)
#        print("check_unprocessed: SQL:\n{}".format(sql))
        cur = self.conn.cursor()
        Found = False
        try:
            cur.execute(sql, (filename,))
            result = cur.fetchone()
        except Exception as e:
            self.logerror("Exception in _query: %s" % e)
        if result and (result[0] > 0):
            print("Skipping  Filename {} as {} in DB".format(filename, column))
            Found = True
        else:
            print("Column {} for Filename {} is not in DB".format(column, filename))
            Found = False
        return Found
    
    
    def logerror(self, msg):
        print("Error (DB): ", msg)

    def index_filenames(self):
        cur = self.conn.cursor()
        try:
            cur.execute("DROP INDEX tag_titles;")
            cur.execute("CREATE INDEX tag_titles ON projects(filename);")
            self.conn.commit()
        except Exception as e:
            self.logerror("Exception in _query: %s" % e)         
        

    def ShowTables(self):
        cur = self.conn.cursor() 
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        available_table=(cur.fetchall())
        [self.ShowStatus(table[0]) for table in available_table]
    #    print("Tables:", available_table)

#Helpful page: https://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html
        
    def ShowStatus(self, table):
        cur = self.conn.cursor() 
        dataCopy = cur.execute("SELECT COUNT(*) FROM " + table)
        values = dataCopy.fetchone()
        print("Table: ", table, " Entries: ", values[0])
    #    print(f'DB File: {dbfile:s}\n');
    #    print(f"{0} Entries in {1}\n" . format(values, table))

    def values_in_col(self, table_name):
        """ Returns a dictionary with columns as keys
        and the number of not-null entries as associated values.
        """
        cursor = self.conn.cursor() 
        cursor.execute('PRAGMA TABLE_INFO({})'.format(table_name))
        info = cursor.fetchall()
        col_dict = dict()
        for col in info:
            col_dict[col[1]] = 0
        for col in col_dict:
            cursor.execute('SELECT ({0}) FROM {1} '
                           'WHERE {0} IS NOT NULL'.format(col, table_name))
            # In my case this approach resulted in a
            # better performance than using COUNT
            number_rows = len(cursor.fetchall())
            col_dict[col] = number_rows
        print("\nNumber of entries per column in table: {}" . format(table_name))
        for i in col_dict.items():
            print('{}: {}'.format(i[0], i[1]))
            return col_dict

    def getCols(self, table):
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA TABLE_INFO({})'.format(table))
        info = [cols[1] for cols in  cursor.fetchall()]
        return(info)

    def SaveCSV(self, table):    
        cursor = self.conn.cursor() 
        cursor.execute(f"SELECT * FROM {table}")
        cols = self.getCols(table)
        print("Cols:", cols)
        with open(self.csv_name + '_' + table + ".csv", "w", newline='') as csv_file:  # Python 3 version    
            csv_writer = csv.writer(csv_file, dialect='excel')
            csv_writer.writerow([i[0] for i in cursor.description]) # write headers
            csv_writer.writerows(cursor)

#Get the pandas Dataframe
    def getDF(self, table, get_again = False):
#        if self.df.empty() or get_again:
#        cursor = self.conn.cursor() 
        self.df = pd.read_sql_query(f"SELECT * FROM {table}", self.conn)
        return self.df

    def FindLoadedCohortsRaw(self, table = 'raw'):
        cursor = self.conn.cursor() 
        cursor.execute("SELECT DISTINCT cohort FROM raw")
        return [element[0] for element in cursor.fetchall()]
    
            
    def db_close(self):
        self.conn.close()


if __name__ == '__main__':
    try:
        DB = Db(str(S.dbfile))
        DB.ShowTables()
        DB.values_in_col('projects')
        DB.values_in_col('raw')
        DB.getCols('projects')
        DB.SaveCSV('projects')
        DB.SaveCSV('raw')
    except Exception as e:
        print("Exception in CM0645 main {}".format(e))
    args = sys.argv[1:]
    if args[0] == "":
        resetting = False  # False # True
    else:
        resetting = True  # False # True
    print("Arg: {}, Reset: {}".format(sys.argv[1:], resetting))
    if resetting:
        DB.initialize()
    else:
        DB.index_filenames()
    DB.ShowStatus('projects')
    DB.ShowStatus('raw')
    DB.getDF('projects')
    print(DB.FindLoadedCohortsRaw('raw'))
    DB.df.describe()
    DB.db_close()

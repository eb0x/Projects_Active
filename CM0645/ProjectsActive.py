from CM0645db import Db
from Data_Prep_v3 import Cohort


basedir = '/home/jeremy/Projects-Active/CM0645/'
#basedir = '/home/izje1/Documents/Projects_Active/'
dbfile = basedir + S.dbfile

def run_cohorts(basedir, DB):
    cohort_15_16 = Cohort("15-16", 'S.cohortdir_15_16S.marksfile_15_16', basedir + 'S.cohortdir_15_16txts/')
    cohort_15_16.describe(" Container of file details and marks")
    cohort_15_16.get_marks()
    cohort_15_16.get_files()
    cohort_15_16.equate_names_marks(DB)
    return([cohort_15_16])
    # cohort_16_17 = Cohort("16-17", 'S.cohortdir_16_17S.marksfile_16_17', basedir + 'S.cohortdir_16_17txts/')
    # cohort_16_17.describe(" Container of file details and marks")
    # cohort_16_17.get_marks()
    # cohort_16_17.get_files()
    # cohort_16_17.equate_names_marks()
    # cohort_17_18 = Cohort("17-18", 'S.cohortdir_17_18CM0645_Marks_17_18_v4.csv', basedir + 'S.cohortdir_17_18txts/')
    # cohort_17_18.describe(" Container of file details and marks")
    # cohort_17_18.get_marks()
    # cohort_17_18.get_files()
    # cohort_17_18.equate_names_marks()


if __name__ == '__main__':
    DB = Db(dbfile)
    DB.ShowTables()
    resetting = False # True # 
    if resetting:
        DB.initialize()
    else:
#        DB.initialize()
        cohorts = run_cohorts(basedir, DB)
        cohorts[0].show()
        print(cohorts)
        DB.index_filenames()
    DB.db_close()

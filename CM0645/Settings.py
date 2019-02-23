import sys, os
from pathlib import Path

scriptpath = sys.path[0]
parent = Path(scriptpath).parent

print("Script path {}, parent {}". format(scriptpath, parent))

basedir = parent #'/home/jeremy/Projects-Active/'
#basedir = '/home/izje1/Documents/Projects_Active/'
dbfile = basedir.joinpath('CM0645.sqlite')

marksfile_15_16 = 'CM0645_Marks_15_16.csv'
cohortdir_15_16 = 'CM0645_Projects_15_16/' 
marksfile_16_17 = 'CM0645_Marks_16_17_v2.csv'
cohortdir_16_17 = 'CM0645_Projects_16_17/'
marksfile_17_18 = 'CM0645_Marks_17_18_v4.csv'
cohortdir_17_18 = 'CM0645_Projects_17_18/'

txts='txts/'
ptxts = 'ptxts/'
taggedtxts = 'taggedtxts/'

BNCfile = "BNC.pickle"

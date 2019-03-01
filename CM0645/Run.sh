#!/bin/sh
python CM0645db.py reset >runlog.txt
python extract_parts_v2.py >>runlog.txt
python Data_Prep_v3.py >>runlog.txt
python New_Readability_stats.py >>runlog.txt
python Token_Tag.py >>runlog.txt


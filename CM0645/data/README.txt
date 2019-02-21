This is a work in progress so expect changes and bugs

db.py:

Database helper class to accumulate metric values. The database is
SQLite.  There is on table: projects.
There are not enough columns. Additional columns should be created for
each metric.

extract_parts.py:

Definitely a work in progress. This uses numerous regexes to get the
free text from the Abastract to the References into a separate file
for text processing.

Data_Prep_v2.py:

This file reconciles the marks spreadsheets with the converted text files
and creates a db entry per student when a project file (txt format) are
associated. Some students have no mark recorded, and some reports can not
be converted to readable text.


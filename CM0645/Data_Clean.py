#Idea behind class is to clean and preprocess data in the DB and then write as csv 
# for further rpocessing
# We remove blank columns, and outliers.

from os import listdir
#from os.path import isfile, join
from pathlib import Path         # python 3 way
import re
import sys
import string
import csv
import pickle
import matplotlib

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from scipy import stats

import pandas as pd
import numpy as np

import Settings as S                    # pathnames
from CM0645db import Db

class Data_Clean:
    df = None

    def __init__(self, db):
        '''Initialize class and get pandas dataframe'''
        self.DB = db
        self.df = DB.getDF('projects')
        self.df.describe()

    def getProjectDataFrames(self):
        #Separate reg, investigative, and SE projects
        #lose first few non-numeric columns
        df = self.df
        self.df100a = df.iloc[:,5:]
        df90 = df.loc[df['Report_Max'] == 90]
        self.df90a = df90.iloc[:,6:]
        df60 = df.loc[df['Report_Max'] == 60]
        self.df60a = df60.iloc[:,6:]
        df40 = df.loc[df['Report_Max'] == 40]
        self.df40a = df40.iloc[:,6:]

    def DataFramesRemoveBlank(self, df):
        #https://stackoverflow.com/questions/21164910/delete-column-in-pandas-if-it-is-all-zeros
        ndf = df.loc[:, (df != 0).any(axis=0)]
        # Drop a row by condition
        ndf2 = ndf[df.AWL_count != 0]
        #remove other nearly empty cols or with minimal data
        #ndf2 = ndf.drop(['tag_LS', 'tag_SYM', 'tag_NNPS', 'tag_UH', 'tag_D'], axis=1)
        return ndf2
       
  #generic normalizer/scaler  assumes all cols numeric
  # #   
    def NormDataFrames(self, df):
        #from sklearn.preprocessing import StandardScaler
        # cols_to_norm = df100a.columns[1:]
        # df100a[cols_to_norm] = MinMaxScaler().fit_transform(df100a[cols_to_norm])
        scaler = MinMaxScaler()
        scaled_values = scaler.fit_transform(df) 
        df.loc[:,:] = scaled_values
        # Remove Outliers
        ndf = df[(np.abs(stats.zscore( df)) < 4).all(axis=1)]
        return ndf

#normalize scale starting at somecol
    def NormSingleDF(self, adf, fromcol=1):
        ndf = adf.iloc[:,5:]            #lose 1st five cols
        ndf2 = self.DataFramesRemoveBlank(ndf)      #remove blank and partial cols
        cols_to_norm = ndf2.columns[fromcol:]       #dont norm project max mark (type)
        ndf2[cols_to_norm] = MinMaxScaler().fit_transform(ndf2[cols_to_norm]) #normalise rest
        # Remove Outliers
        ndf3 = ndf2[(np.abs(stats.zscore( ndf2)) < 4).all(axis=1)]
        ndf3.insert(1, 'uid', self.df['uid'])       # replace uid
        return ndf3

#get row stripped out and save for checking
    def RemovedRows(self, ndf):
        removed_rows = self.df[~self.df.index.isin(ndf.index)]
        removed_rows.to_csv('removed_rows.csv')
        
    def DescribeDFs(self):
        self.df100a.describe()
        print(self.df90a.describe())
        self.df60a.describe()
        self.df40a.describe()
        

if __name__ == "__main__":
    dbfile = S.basedir / S.dbfile
    DB = Db(dbfile)
    DC = Data_Clean(DB)
    DC.getProjectDataFrames()
    df90b = DC.DataFramesRemoveBlank(DC.df90a)
    df90c = DC.NormDataFrames(df90b)
    df90c.to_csv("testout.csv")
    ndf5 = DC.NormSingleDF(DC.df)
    ndf5.to_csv("testoutdf100.csv")
    DC.RemovedRows(ndf5)
 #   df100_Normed.insert(1, 'uid', df['uid'])

import pandas as pd
import os
import numpy as np
import sys


if __name__ == '__main__':


    ############ Setup variables for current study #####
    ####################################################
    #Set Behavioral and functional data paths
    behavdatapath = '/home/jagust/DST/BehavioralData'
    subjectlist = '/home/jagust/DST/Scanned_Subjects.csv'
    allsubs = pandas.read_csv(subjectlist, sep=None)
    datafilename = '%s_Data.csv'
    retrievalfilename = '%s_RetrievalPerformance.csv'
    outname = '%s_RetrievalPerformanceRT.csv'
    ####################################################
    
    for subj in allsubs.Subject:
        datafile = os.path.join(behavdatapath, subj, datafilename%(subj))
        retrievalfile = os.path.join(behavdatapath, subj, retrievalfilename%(subj))
        try:
            datadat = pd.read_csv(datafile, sep=None)
            retrievaldat = pd.read_csv(retrievalfile, sep=None)
            rtdat = datadat[['NewCode','RT']]
            retrievalrt = pd.merge(retrievaldat, rtdat, how='left', on='NewCode')
            outfile = os.path.join(behavdatapath, subj, outname%(subj))
            retrievalrt.to_csv(outfile, index=False)
        except:
            print subj, 'does not exist'

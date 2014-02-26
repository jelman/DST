#!/usr/bin/env python
import pandas
import os
import numpy as np
import sys
from glob import glob

"""
Saves out retrieval performance for all subjects listed in IncludedSubjects.csv
"""

def SaveOutfile(frame,filename,pth,index):
        outfile = os.path.join(pth,filename)
        frame.to_csv(outfile,index=index,header=True)
        print 'Saved %s'%outfile
    
def CalcConf(resp):
    if (resp == 1 or resp == 4):
        return 'Hi'
    elif (resp == 2 or resp == 3):
        return 'Lo'
    else:
        return ''

if __name__ == '__main__':


    ############ Setup variables for current study #####
    ####################################################
    #Set Behavioral and functional data paths
    behavdatapath = '/home/jagust/DST/BehavioralData'
    subjectlist = '/home/jagust/DST/Scanned_Subjects.csv'
    cols = ['Subject','Group','NewCode','OldNew','GistSlide.ACC','DetailSlide.ACC','Confidence','RT']
    file_suffix = '_RetrievalPerformanceRT.csv'
    ###################################################
    #Load list of subjects. Split into old and young subject lists.
    allsubs = pandas.read_csv(subjectlist, sep=None)
    youngsubs = allsubs['Subject'][allsubs['Group']=='Young']
    oldsubs = allsubs['Subject'][allsubs['Group']=='Old']
    #Load in young subject to dataframe.
    youngdat = pandas.DataFrame()
    for subj in youngsubs:
        filename = subj + file_suffix
        infile = os.path.join(behavdatapath,subj,filename)
        if os.path.exists(infile):
            subjdat = pandas.read_csv(infile, sep=',')
            youngdat = youngdat.append(subjdat, ignore_index=True)
        else:
            print "%s behavioral data not found"%(subj)
    youngdat['Group'] = 'young'

#Load in old subjects to dataframe
    olddat = pandas.DataFrame()
    for subj in oldsubs:
        filename = subj + file_suffix
        infile = os.path.join(behavdatapath,subj,filename)
        if os.path.exists(infile):
            subjdat = pandas.read_csv(infile, sep=',')
            olddat = olddat.append(subjdat, ignore_index=True)
        else:
            print "%s behavioral data not found"%(subj)
    olddat['Group'] = 'old'

#Combine both groups into dataframe and save out
    combinedat = youngdat.append(olddat, ignore_index=True)
    combinedat['Confidence'] = [CalcConf(resp) for resp in combinedat['GistSlide.RESP']]
    alldat = combinedat
    alldat = combinedat.reindex(columns=cols)
    outfilename = 'DST_RetrievalPerformance.csv'
    SaveOutfile(alldat,outfilename,behavdatapath,index=False)

#Generate summary of gist performance and save out.
    gistout = 'GistPerformance.csv'    
    gistpivot = pandas.pivot_table(alldat,values='GistSlide.ACC',
                                    rows=['Group','Subject'],cols='OldNew')
    SaveOutfile(gistpivot,gistout,behavdatapath,index=True)

#Generate summary of detail performance and save out.
    gistcorr = alldat[alldat['GistSlide.ACC']==1]
    detailpivot = pandas.pivot_table(gistcorr,values='DetailSlide.ACC',rows=['Group','Subject'])
    detailout = 'DetailPerformance.csv'
    SaveOutfile(detailpivot,detailout,behavdatapath,index=True)





    



    

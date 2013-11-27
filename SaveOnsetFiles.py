#!/usr/bin/env python
import csv
import numpy as np
import sys, os
import pandas

"""
Saves out individual condition onset files into subject folders. 
Takes subject ID as command line argument.
"""
def SaveOut(frame,subj,run,condition,pth='/home/jagust/DST/FSL/functional'):
	filename = subj + '_' + run + '_' + condition + '.txt'
	outfile = os.path.join(pth,subj,run,filename)
	outframe = frame[onset_cols]
	np.savetxt(outfile,outframe,delimiter='\t',fmt='%.3f %.1f %i')
	print 'Saved %s'%outfile

def SaveDetails(runframe,subj,run,acc,gistacc,detail_bins):
	#Loop over all detail conditions and save out stim schedules to functional folders.
	for det in detail_bins.keys():
		detframe = runframe[(runframe['GistSlide.ACC']==gistacc) & 
							runframe['DetailSlide.ACC'].isin(detail_bins[det])]        		
		condition = acc + '_' + str(det) 
		SaveOut(detframe,subj,run,condition)
    		
    	#Create array and save stim schedules for Gist correct, high confidence.
def SaveGist(runframe,subj,run,acc,gistacc):
    if gistacc == 1:
	    for conf in ['Hi','Lo']:
		    confframe = runframe[(runframe['GistSlide.ACC']==gistacc) & 
			    (runframe['Confidence']==conf)]
		    condition = acc + '_' + conf
		    SaveOut(confframe,subj,run,condition)  
    if gistacc == 0:
        confframe = runframe[runframe['GistSlide.ACC']==gistacc]
        condition = acc
        SaveOut(confframe,subj,run,condition)

if __name__ == '__main__':

    if len(sys.argv) ==1:
        print 'USAGE: python SaveOnsetFiles.py Bxx-xxx Bxx-xxx Bxx-xxx'
    else:
        args = sys.argv[1:]
    #Set up paths for current study
    ####################################################
	behavdatapath = '/home/jagust/DST/BehavioralData'
	funcdatapath = '/home/jagust/DST/FSL/functional'
	onset_cols = ['Onset','Duration','Weight']
	detail_bins = {'Low':[0,1,2],'Med':[3],'High':[4,5,6]}
    ####################################################

	for subj in args:
		subjdir = os.path.join(behavdatapath,subj)
		filename = subj + '_Data.csv'
		infile = os.path.join(behavdatapath,subjdir,filename)
		data = pandas.read_csv(infile,sep=',')
		#Loop over all runs
		for run in ['run01', 'run02', 'run03']:
			runframe = data[data['Run']==run]
			#Loop over Gist correct and incorrect
			for acc in ['Incorrect','Correct']:
				if 'Correct' in acc:
				    gistacc=1
				elif 'Incorrect' in acc:
				    gistacc=0    
				#SaveDetails(runframe,subj,run,acc,gistacc,detail_bins)
				SaveGist(runframe,subj,run,acc,gistacc)

import os, sys
import pandas as pd
from glob import glob
import collections
import matplotlib.pyplot as plt

def parse_report(fqdir, statnames):
    infile = os.path.join(fqdir, 'report.txt')
    fqreport = pd.read_csv(infile, header=None,delimiter='\s',names=['nSubs','stat','nVoxels','min','10pct',
    'mean','median','90pct','max','stdev','voxX','voxY','voxZ','mmX','mmY','mmZ'])
    fqreport_rename = fqreport.set_index('stat')
    zreport = fqreport_rename.ix[['zstat' in x for x in fqreport_rename.index]]
    zreport = zreport.rename(index=
                                collections.OrderedDict(zip(zreport.index, stat_names)))
    copereport = fqreport_rename.ix[['cope' in x for x in fqreport_rename.index]]
    copereport = copereport.rename(index=
                                collections.OrderedDict(zip(copereport.index, stat_names)))
    return zreport, copereport
    
    

##########################################################################
        
if __name__ == '__main__':


    if len(sys.argv) == 1:
        print 'USAGE: CreateFeatquery.py <featquery dir name> <subject 1> <subject 2> ...'
    else:
        fqdirname = sys.argv[1]
        sublist = sys.argv[2:]
        
    basedir = '/home/jagust/DST/FSL/functional'
    outdir = '/home/jagust/DST/FSL/results'
    stat_names = ['Details1', 'Details2', 'Details3', 'Details4', 'Details5']
    # Specify group membership if available, otherwise set to None
    groupinfo = pd.read_csv('/home/jagust/DST/FSL/spreadsheets/Included_Subjects.csv', sep=None, index_col=0)
    groupinfo = groupinfo['Status']
    outname = os.path.join(outdir, fqdirname.strip('featquery_'))
    
    # Create empty dataframes to hold full results
    zmeandf = pd.DataFrame(index=stat_names)
    zmaxdf = pd.DataFrame(index=stat_names)
    copemeandf = pd.DataFrame(index=stat_names)
    copemaxdf = pd.DataFrame(index=stat_names)
    
    for subj in sublist:
        print 'Starting on subject %s'%(subj)
        globstr = os.path.join(basedir, 
                                '2ndLevel/Details',
                                subj + '.gfeat',
                                'cope1.feat',
                                fqdirname)
        fqdir = glob(globstr)[0]
        zreport, copereport = parse_report(fqdir, stat_names)
        
        if not zreport.empty:
            zmeandf[subj] = zreport['mean']
            zmaxdf[subj] = zreport['max']       
        if not copereport.empty:
            copemeandf[subj] = copereport['mean']
            copemaxdf[subj] = copereport['max']

        
    if not zmeandf.empty:
        zmeandfT = zmeandf.T
        zmeandfT.insert(0, 'Status', groupinfo)
        zmeandfT.to_csv(outname + '_zmean.csv', sep='\t', index=True, index_label='Subject')
        zmean_grp = zmeandfT.groupby(by='Status')            
     
    if not zmaxdf.empty:            
        zmaxdfT = zmaxdf.T
        zmaxdfT.insert(0, 'Status', groupinfo)
        zmaxdfT.to_csv(outname + '_zmax.csv', sep='\t', index=True, index_label='Subject')
        zmax_grp = zmaxdfT.groupby(by='Status')
   
    if not copemeandf.empty:
        copemeandfT = copemeandf.T
        copemeandfT.insert(0, 'Status', groupinfo)
        copemeandfT.to_csv(outname + '_copemean.csv', sep='\t', index=True, index_label='Subject')
        copemean_grp = copemeandfT.groupby(by='Status')
     
    if not copemaxdf.empty:    
        copemaxdfT = copemaxdf.T
        copemaxdfT.insert(0, 'Status', groupinfo)
        copemaxdfT.to_csv(outname + '_copemax.csv', sep='\t', index=True, index_label='Subject')
        copemax_grp = copemaxdfT.groupby(by='Status')

        
    fig, axes = plt.subplots(nrows=2, ncols=2)
    zmean_grp.mean().T.plot(ax=axes[0,0], title='Z mean', marker='o', legend=False)
    zmax_grp.mean().T.plot(ax=axes[0,1], title='Z max', marker='o', legend=False)
    copemean_grp.mean().T.plot(ax=axes[1,0], title='Cope Mean', marker='o', legend=False)
    copemax_grp.mean().T.plot(ax=axes[1,1], title='Cope Max', marker='o')
    leg = plt.legend(bbox_to_anchor=(0, 0, 1, 1), bbox_transform=plt.gcf().transFigure, fancybox=True)
    leg.get_frame().set_alpha(0.7)
    plt.tight_layout()
    plt.savefig(outname + '.png')

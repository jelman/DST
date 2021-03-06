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
                                collections.OrderedDict(zip(zreport.index, statnames)))
    copereport = fqreport_rename.ix[['cope' in x for x in fqreport_rename.index]]
    copereport = copereport.rename(index=
                                collections.OrderedDict(zip(copereport.index, statnames)))
    return zreport, copereport
    
def pandas_bar_subplot(df, ax, title):
    y = df.mean().values.T[0]
    N = len(y)
    ind = range(N)
    err = df.std().values.T[0]
    ax.bar(ind, y, facecolor='#777777', width=0.3,
           align='center', yerr=err, ecolor='black')
    ax.set_ylabel('Contrast value')
    ax.set_title(title,fontstyle='italic')
    ax.set_xticks(ind)
    group_labels = df.groups.keys()
    ax.set_xticklabels(group_labels)
    ax.grid()
    fig.autofmt_xdate()
    
    

##########################################################################
        
if __name__ == '__main__':

    ################################################################################
    if len(sys.argv) == 1:
        print 'USAGE: CreateFeatquery.py <featquery dir name> <subject 1> <subject 2> ...'
    else:
        fqdirname = sys.argv[1]
        sublist = sys.argv[2:]
        
    basedir = '/home/jagust/DST/FSL/functional'
    secondleveldir = os.path.join(basedir, '2ndLevel', 'Gist')
    outdir = '/home/jagust/DST/FSL/results/Gist'
    stat_names = ['HiCorr gt Incorr']
    reverse_cols = False #Should column order be reversed for plotting?
    # Specify group membership if available, otherwise set to None
    groupinfo = pd.read_csv('/home/jagust/DST/FSL/spreadsheets/Included_Subjects.csv', sep=None, index_col=0)
    groupinfo = groupinfo['Status']
    outname = os.path.join(outdir, fqdirname.strip('featquery_'))
    #############################################################################

    # Create empty dataframes to hold full results
    zmeandf = pd.DataFrame(index=stat_names)
    zmaxdf = pd.DataFrame(index=stat_names)
    copemeandf = pd.DataFrame(index=stat_names)
    copemaxdf = pd.DataFrame(index=stat_names)
    
    for subj in sublist:
        print 'Starting on subject %s'%(subj)
        globstr = os.path.join(secondleveldir,
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

    if reverse_cols == True:
        col_names = list(reversed(stat_names))
    else:
        col_names = stat_names
        
    if not zmeandf.empty:
        zmeandfT = pd.DataFrame(zmeandf.T, columns=col_names)
        zmeandfT.insert(0, 'Status', groupinfo)
        zmeandfT.to_csv(outname + '_zmean.csv', sep='\t', index=True, index_label='Subject')
        zmean_grp = zmeandfT.groupby(by='Status')            
     
    if not zmaxdf.empty:            
        zmaxdfT = pd.DataFrame(zmaxdf.T, columns=col_names)
        zmaxdfT.insert(0, 'Status', groupinfo)
        zmaxdfT.to_csv(outname + '_zmax.csv', sep='\t', index=True, index_label='Subject')
        zmax_grp = zmaxdfT.groupby(by='Status')
   
    if not copemeandf.empty:
        copemeandfT = pd.DataFrame(copemeandf.T, columns=col_names)
        copemeandfT.insert(0, 'Status', groupinfo)
        copemeandfT.to_csv(outname + '_copemean.csv', sep='\t', index=True, index_label='Subject')
        copemean_grp = copemeandfT.groupby(by='Status')
     
    if not copemaxdf.empty:    
        copemaxdfT = pd.DataFrame(copemaxdf.T, columns=col_names)
        copemaxdfT.insert(0, 'Status', groupinfo)
        copemaxdfT.to_csv(outname + '_copemax.csv', sep='\t', index=True, index_label='Subject')
        copemax_grp = copemaxdfT.groupby(by='Status')

        
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2)
    pandas_bar_subplot(zmean_grp, ax1, 'Z mean')
    pandas_bar_subplot(zmax_grp, ax2, 'Z max')
    pandas_bar_subplot(copemean_grp, ax3, 'Cope mean')
    pandas_bar_subplot(copemax_grp, ax4, 'Cope max')
    plt.tight_layout()
    plt.savefig(outname + '.png')

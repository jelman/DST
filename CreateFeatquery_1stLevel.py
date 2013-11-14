import os, sys
import pandas as pd
from glob import glob
import collections
import matplotlib.pyplot as plt

def parse_report(fqdir, statnames):
    infile = os.path.join(fqdir, 'report.txt')
    fqreport = pd.read_csv(infile, header=None,delimiter='\s')
    fqreport.pop('X0')
    mycols = collections.OrderedDict([('X1', 'stat'), ('X2', 'numvoxels'), 
    ('X3', 'min'), ('X4', '10pct'), ('X5', 'mean'), ('X6', 'median'), 
    ('X7', '90pct'), ('X8', 'max'), ('X9', 'stddev'), ('X10', 'voxX'), 
    ('X11', 'voxY'), ('X12', 'voxZ'), ('X13', 'mmX'), ('X14', 'mmY'), 
    ('X0', 'stat'), ('X15', 'mmZ')])
    fqreport_rename = fqreport.rename(columns=mycols)
    fqreport_rename = fqreport_rename.set_index('stat')
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
    groupinfo = pd.read_csv('/home/jagust/DST/Included_Subjects.csv', sep=None, index_col=0)
    groupinfo = groupinfo['GROUP']
    groupinfo = groupinfo.str.replace('old.*', 'old')
    outname = os.path.join(outdir, fqdirname.strip('featquery_'))
    
    # Create empty dataframes to hold full results
    zmeandf = pd.DataFrame(columns=stat_names)
    zmaxdf = pd.DataFrame(columns=stat_names)
    copemeandf = pd.DataFrame(columns=stat_names)
    copemaxdf = pd.DataFrame(columns=stat_names)
    
    for subj in sublist:
        globstr = os.path.join(basedir, 
                                subj,
                                'run0*',
                                'Detail.feat',
                                fqdirname)
        fqdirs = glob(globstr)
        for fqrundir in fqdirs:
            run = re.search('run..', fqrundir).group()
            zreport, copereport = parse_report(fqrundir, stat_names)

            if not zreport.empty:
                submean = zreport['mean']
                submean.name = subj
                zmeandf = zmeandf.append(submean)
                zmeandf['Run'] = run    
                submax = zreport['max']
                submax.name = subj
                zmaxdf = zmaxdf.append(submax)
                zmaxdf['Run'] = run   
            if not copereport.empty:
                submean = copereport['mean']
                submean.name = subj
                copemeandf = copemeandf.append(submean)
                copemeandf['Run'] = run    
                submax = copereport['max']
                submax.name = subj
                copemaxdf = copemaxdf.append(submax)
                copemaxdf['Run'] = run  

        
    if not zmeandf.empty:
        zmeandfT = zmeandf.T
        zmeandfT.insert(0, 'Group', groupinfo)
        zmeandfT.to_csv(outname + '_zmean.csv', sep='\t', index=True, index_label='Subject')
        zmean_grp = zmeandfT.groupby(by='Group')            
     
    if not zmaxdf.empty:            
        zmaxdfT = zmaxdf.T
        zmaxdfT.insert(0, 'Group', groupinfo)
        zmaxdfT.to_csv(outname + '_zmax.csv', sep='\t', index=True, index_label='Subject')
        zmax_grp = zmaxdfT.groupby(by='Group')
   
    if not copemeandf.empty:
        copemeandfT = copemeandf.T
        copemeandfT.insert(0, 'Group', groupinfo)
        copemeandfT.to_csv(outname + '_copemean.csv', sep='\t', index=True, index_label='Subject')
        copemean_grp = copemeandfT.groupby(by='Group')
     
    if not copemaxdf.empty:    
        copemaxdfT = copemaxdf.T
        copemaxdfT.insert(0, 'Group', groupinfo)
        copemaxdfT.to_csv(outname + '_copemax.csv', sep='\t', index=True, index_label='Subject')
        copemax_grp = copemaxdfT.groupby(by='Group')

        
    fig, axes = plt.subplots(nrows=2, ncols=2)
    zmean_grp.mean().T.plot(ax=axes[0,0], title='Z mean', marker='o', legend=False)
    zmax_grp.mean().T.plot(ax=axes[0,1], title='Z max', marker='o', legend=False)
    copemean_grp.mean().T.plot(ax=axes[1,0], title='Cope Mean', marker='o', legend=False)
    copemax_grp.mean().T.plot(ax=axes[1,1], title='Cope Max', marker='o')
    plt.legend(bbox_to_anchor=(0, 0, 1, 1), bbox_transform=plt.gcf().transFigure)
    plt.tight_layout()
    plt.savefig(outname + '.png')

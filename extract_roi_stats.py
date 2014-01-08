import os
import numpy as np
import pandas as pd
from nipype.interfaces.fsl import ImageStats 
import matplotlib.pyplot as plt
import seaborn as sns
import general_utilities as gu

def fslstats(infile, mask):
    """
    Wrapper for fslstats. Takes input file and extract mean from specified ROI mask
    """
    stats = ImageStats()
    stats.inputs.in_file = infile
    stats.inputs.op_string = '-k %s -M'
    stats.inputs.mask_file = mask
    cout = stats.run()
    return cout.outputs.out_stat

def plot_line(df, title, xticklabels, outfile):
    sns.set(style="darkgrid", context="poster")
    ax = df.plot(title=title, marker='o')
    ax.set_ylabel('Z Score')
    ax.set_xticks(range(len(xticklabels)))
    ax.set_xticklabels(xticklabels)
    plt.tight_layout()
    plt.legend(loc='best', fancybox=True).get_frame().set_alpha(0.7)
    plt.savefig(outfile)
    
def plot_bar(df, title, outfile):
    sns.set(style="darkgrid", context="poster")
    ax = df.plot(kind='bar', sort_columns=False, title=title)
    ax.set_ylabel('Z Score')
    plt.tight_layout()
    # Shink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fancybox=True)
    plt.savefig(outfile)
    
    
if __name__ == '__main__':

    ###################### Set inputs ##################################
    sublist_file = '/home/jagust/DST/FSL/spreadsheets/AGE_Effect_Subs.txt' #List of subjects
    mask = '/home/jagust/DST/FSL/masks/Gist/TaskPos_AGE_Tmap2.nii.gz' #ROI mask
    statlist = ['zstat1', 'zstat2', 'zstat5'] #Stats to extract
    groupinfo_file = '/home/jagust/DST/FSL/spreadsheets/Included_Subject_Covariates.csv' #File listing group status
    infile_pattern = '/home/jagust/DST/FSL/functional/2ndLevel/Gist_ST/%s.gfeat/cope1.feat/stats/%s.nii.gz'
    outfile_pattern = '/home/jagust/DST/FSL/results/Gist/%s.csv'
    #Specifiy plot info below if desired
    plot_fig = 'line' #Specify type of figure ('bar' or 'line')
    plotcols = statlist
    col_labels = ['Hi Hit','Miss','Hi Hit>Miss']
    plt_outfile_pattern = '/home/jagust/DST/FSL/results/Gist/%s.png'
    #Specify info to extract GM values
    gm_pattern = '/home/jagust/DST/FSL/functional/%s/run02/Detail_ST.feat/reg/highresGMs2standard.nii.gz'   
    ####################################################################

    #Load subject list and group info file
    with open(sublist_file,'r+') as f:
        sublist = f.read().splitlines()        
    groupinfo = pd.read_csv(groupinfo_file, sep=None)  
    
    #Set output file names
    pth, mask_name, ext = gu.split_filename(mask)
    outfile = outfile_pattern%(mask_name)
    if plot_fig:
        plt_outfile = plt_outfile_pattern%(mask_name)
    #Extract stats from functional data  
    statdict = {}
    for stat in statlist:
        statdict[stat] = {}
        for subj in sublist:
            stat_infile = infile_pattern%(subj,stat)
            subjstat = fslstats(stat_infile, mask)
            statdict[stat][subj] = subjstat
    statdf = pd.DataFrame.from_dict(statdict)
    statdf = statdf.reindex(columns=statlist) #re-order columns to match statlist above
    
    #Extract GM values
    gmdict = {}
    for subj in sublist:
        print subj
        gm_infile = gm_pattern%(subj)
        subjstat = fslstats(gm_infile, mask)
        gmdict[subj] = subjstat   
    gmdict = {'GM':gmdict} 
    gmdf = pd.DataFrame.from_dict(gmdict, orient='columns')

    
    #Join functional and GM values with group info
    statdf_groupinfo = groupinfo.join(statdf, on='Subject', how='right')  
    statdf_groupinfo = pd.merge(statdf_groupinfo, gmdf, left_on='Subject', right_index=True)  
    statdf_groupinfo.to_csv(outfile, header=True, index=False, sep=',')
    
    #Plot and save figure
    if plot_fig == 'line': 
        statdf_grp = statdf_groupinfo.groupby(by='Group')
        plot_line(statdf_grp.mean()[plotcols].T, mask_name, col_labels, plt_outfile)
    else:
        for i in range(len(plotcols)):
            column_mapper[plotcols[i]] = col_labels[i]
        statdf_groupinfo = statdf_groupinfo.rename(columns=column_mapper)
        statdf_grp = statdf_groupinfo.groupby(by='Group')
        plot_bar(statdf_grp.mean()[col_labels], mask_name, plt_outfile)        

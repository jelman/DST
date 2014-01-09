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

def plot_line(df, xticklabels, outfile, title=None):
    sns.set(style="darkgrid", context="poster")
    ax = df.plot(title=title, marker='o')
    ax.set_ylabel('Z Score')
    ax.set_xticks(range(len(xticklabels)))
    ax.set_xticklabels(xticklabels)
    plt.tight_layout()
    plt.legend(loc='best', prop={'size':12}, fancybox=True).get_frame().set_alpha(0.7)
    plt.savefig(outfile)
    
    
def plot_pyplot_bar(df, error, outfile, title=None):    
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #sns.set(style="darkgrid", context="poster")
    sns.set(style="ticks", context="poster")
    N = len(df)
    width = 0.25
    ind = np.arange(N) + width/2

    groups = len(df.ix[0])
    for group in range(groups):
        groupind = ind + (group * width)
        rects = ax.bar(groupind, df.iloc[:,group], width,
                    color=sns.color_palette()[group], 
                    label=col_labels[group],
                    yerr=error.iloc[:,group],
                    error_kw=dict(capsize=5))
    ax.set_ylabel('Z Score')
    ax.set_xlabel('Group')
    ax.set_xticks(ind+width)
    ax.set_xticklabels(df.index)
    if title:
        ax.set_title(title)
    plt.tight_layout()
    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(handles, labels, loc='best', prop={'size':12}, fancybox=True).get_frame().set_alpha(0.7)
    ax.axhline(color='black', linestyle='--')
    sns.despine()
    plt.savefig(outfile)    
   
def plot_pandas_bar(df, error, outfile, title=None):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    sns.set(style="darkgrid", context="poster")
    df.plot(kind='bar', ax=ax, sort_columns=False)
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
    sublist_file = '/home/jagust/DST/FSL/spreadsheets/PIB_Effect_Subs.txt' #List of subjects
    mask = '/home/jagust/DST/FSL/masks/Gist/TaskPos_PIB_Tmap2.nii.gz' #ROI mask
    statlist = ['zstat1', 'zstat2', 'zstat5'] #Stats to extract
    groupinfo_file = '/home/jagust/DST/FSL/spreadsheets/Included_Subject_Covariates.csv' #File listing group status
    infile_pattern = '/home/jagust/DST/FSL/functional/2ndLevel/Gist_ST/%s.gfeat/cope1.feat/stats/%s.nii.gz'
    outfile_pattern = '/home/jagust/DST/FSL/results/Gist/%s.csv'
    #Specifiy plot info below if desired
    plot_fig = 'bar' #Specify type of figure ('bar' or 'line')
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
        column_mapper = {}
        statdf_grp = statdf_groupinfo.groupby(by='Group')
        plot_line(statdf_grp.mean()[plotcols].T, 
                    col_labels, 
                    plt_outfile)
    else:
        column_mapper = {}
        for i in range(len(plotcols)):
            column_mapper[plotcols[i]] = col_labels[i]
        statdf_groupinfo = statdf_groupinfo.rename(columns=column_mapper)
        statdf_grp = statdf_groupinfo.groupby(by='Group')
        plot_pyplot_bar(statdf_grp.mean()[col_labels], 
                        statdf_grp.std()[col_labels], 
                        plt_outfile)        

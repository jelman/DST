import os, re
from glob import glob
import numpy as np
import pandas as pd
from nipype.interfaces.fsl import ImageStats 
import matplotlib.pyplot as plt
import seaborn as sns
import general_utilities as gu


def subject_mean(df, key):
    grouped_df = df.groupby(key)
    return grouped_df.aggregate(np.mean)
    
    
def get_sess_name(instr, pattern='run[0-9]{2}'):
    """regexp to find pattern in string
    default pattern = runXX  X is [0-9]
    """
    m = re.search(pattern, instr)
    try:
        sess_name = m.group()
    except:
        print pattern, ' not found in ', instr
        sess_name = None
    return sess_name


def create_nested_df(user_dict):
    """
    Create heirarchical dataframe from nested dictionary. Currently works for 
    three levels. First key will be first level index, second key will be
    second level index, and third key will be set as columns.
    """
    subidlist = []
    frames = []
    for subid, d in user_dict.iteritems():
        subidlist.append(subid)
        frames.append(pd.DataFrame.from_dict(d, orient='index'))
    user_df = pd.concat(frames, keys=subidlist)
    return user_df
   
   
def extract_first_level(statlist, sublist, infile_pattern, mask):
    statdict = {}
    for subj in sublist:
        statdict[subj] = {}
        sess_glob = infile_pattern%(subj,'run*', statlist[0])
        sess_list = glob(sess_glob)
        for sess in sess_list:
            sess_name = get_sess_name(sess)
            statdict[subj][sess_name] = {}
            for stat in statlist:
                statdict[subj][sess_name][stat] = {}
                stat_file = infile_pattern%(subj,sess_name, stat)
                sess_stat = fslstats(stat_file, mask)
                statdict[subj][sess_name][stat] = sess_stat
    statdf = create_nested_df(statdict)
    statdf.index.names = ['Subject', 'Session']
    statdf = statdf[statlist] #re-order columns to match statlist above
    statdf = statdf.reset_index()
    return statdf

def extract_second_level(statlist, sublist, infile_pattern, mask):
    statdict = {}
    for stat in statlist:
        statdict[stat] = {}
        for subj in sublist:
            stat_infile = infile_pattern%(subj,stat)
            subjstat = fslstats(stat_infile, mask)
            statdict[stat][subj] = subjstat
    statdf = pd.DataFrame.from_dict(statdict)
    statdf = statdf[statlist] #re-order columns to match statlist above
    return statdf

def run_first_level(statlist, sublist, infile_pattern, mask):    
    statdf = extract_first_level(statlist, sublist, infile_pattern, mask)
    statdf_sub_mean = subject_mean(statdf, 'Subject')
    #Join functional and GM values with group info
    statdf_groupinfo = groupinfo.join(statdf_sub_mean, on='Subject', how='right')  
    statdf_groupinfo = pd.merge(statdf_groupinfo, gmdf, left_on='Subject', right_index=True)  
    statdf_groupinfo.to_csv(outfile, header=True, index=False, sep=',')
    return statdf_groupinfo
        
            
def run_second_level(statlist, sublist, infile_pattern, mask):    
    statdf = extract_second_level(statlist, sublist, infile_pattern, mask)
    #Join functional and GM values with group info
    statdf_groupinfo = groupinfo.join(statdf, on='Subject', how='right')  
    statdf_groupinfo = pd.merge(statdf_groupinfo, gmdf, left_on='Subject', right_index=True)  
    statdf_groupinfo.to_csv(outfile, header=True, index=False, sep=',')
    return statdf_groupinfo
        
            
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
    sns.set(style="ticks", context="poster")
    ax = df.plot(title=title, marker='o')
    ax.set_ylabel('Z Score')
    ax.set_xticks(range(len(xticklabels)))
    ax.set_xticklabels(xticklabels)
    plt.tight_layout()
    plt.legend(loc='best', prop={'size':12}, fancybox=True).get_frame().set_alpha(0.7)
    sns.despine()
    plt.savefig(outfile)
    
def plot_scatter(df, x, y, xticklabels, outfile, title=None):
    sns.set(style="ticks", context="poster")
    sns.lmplot(x, y, df, color='Group', 
                palette="muted", x_jitter=.15, x_partial=['Age','GM'], 
                scatter_kws=dict(marker='o'))

    plt.xticks(arange(7), xticklabels)
    plt.xlabel(x, fontweight='bold')
    plt.ylabel(y, fontweight='bold')
    plt.tight_layout()
    plt.legend(loc='best', fancybox=True).get_frame().set_alpha(0.7)
    sns.despine()   
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
    sublist_file = '/home/jagust/DST/FSL/spreadsheets/AllSubs.txt' #List of subjects
    mask = '/home/jagust/DST/FSL/masks/Left_Hippo_maxprob25.nii.gz' #ROI mask
    statlist = ['zstat1', 'zstat2', 'zstat3', 'zstat4', 'zstat5'] #Stats to extract
    groupinfo_file = '/home/jagust/DST/FSL/spreadsheets/Included_Subject_Covariates.csv' #File listing group status
    infile_pattern = '/home/jagust/DST/FSL/functional/2ndLevel/Details_ST/%s.gfeat/cope1.feat/stats/%s.nii.gz'
    stat_level = 2
    outfile_pattern = '/home/jagust/DST/FSL/results/Details/%s.csv'
    #Specifiy plot info below if desired
    plot_fig = 'line' #Specify type of figure ('bar' or 'line')
    plotcols = statlist
    col_labels = ['Detail1', 'Detail2', 'Detail3', 'Detail4', 'Detail5']
    plt_outfile_pattern = '/home/jagust/DST/FSL/results/Details/%s.png'
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
        
    #Extract GM values
    gmdict = {}
    for subj in sublist:
        print subj
        gm_infile = gm_pattern%(subj)
        subjstat = fslstats(gm_infile, mask)
        gmdict[subj] = subjstat   
    gmdict = {'GM':gmdict} 
    gmdf = pd.DataFrame.from_dict(gmdict, orient='columns')
    
    #Extract stats from functional data  
    if not (stat_level == 1 or stat_level == 2):
        print  "Level to extract values from not specified"
    elif stat_level == 2:   
        statdf_groupinfo = run_second_level(statlist, sublist, infile_pattern, mask)

    elif stat_level == 1:
        statdf_groupinfo = run_first_level(statlist, sublist, infile_pattern, mask)


    
    #Plot and save figure
    if plot_fig == 'line': 
        statdf_grp = statdf_groupinfo.groupby(by='Group')
        plot_line(statdf_grp.mean()[plotcols].T, 
                    col_labels, 
                    plt_outfile)
    elif:
        longdf = pd.melt(statdf_groupinfo, id_vars=['Subject','Group','PIB_Index', 'Age', 'GM'], 
                    value_vars=statlist, 
                    var_name='Detail Level', 
                    value_name='Z score')
        longdf['Detail Level'] = longdf['Detail Level'].str.replace('zstat','').astype('int')
        ticklabels = range(1,len(statlist)+1)
        ticklabels.insert(0,'')
        ticklabels.append('')   
        plot_scatter(longdf, 'Detail Level', 'Z score', ticklabels, outfile, title=None)           
               
    else:
        column_mapper = {}
        for i in range(len(plotcols)):
            column_mapper[plotcols[i]] = col_labels[i]
        statdf_renamed = statdf_groupinfo.rename(columns=column_mapper)
        statdf_grp = statdf_renamed.groupby(by='Group')
        plot_pyplot_bar(statdf_grp.mean()[col_labels], 
                        statdf_grp.std()[col_labels], 
                        plt_outfile)        

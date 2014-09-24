import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
%pylab

"""
Plotting script for DST study. Plots linear slope values from Details task against PIB Index.
PIB- subjects are displayed as a box plot, as any variation around 1.0 is presumed to 
represent noise (or at least there is not enough meaningful representation to fit a 
regression slope. A regression slope is fit to the PIB+ subjects.  
"""

infile = '/home/jagust/DST/FSL/results/Details/Details_PIB_ParametricPos_TaskPos_TaskNeg.csv'
outfile = '/home/jagust/DST/FSL/results/Details/Details_PIBpos_PIBIndex_Taskpos_boxplot.tif'

dat = pd.read_csv(infile)
dat_pibpos = dat[dat.Group=='Old PIB+']
dat_pibneg = dat[dat.Group=='Old PIB-']
dat_pibneg = dat_pibneg.rename(columns={'TaskPos':1.0})
sns.set(style="ticks", context="poster", palette='Set1')

#### PIB- boxplot ########
ax1 = plt.boxplot(dat_pibneg[1.0].values, widths=.08)
sns.regplot("PIB_Index", "TaskPos", dat_pibneg, ci=False, truncate=True, 
    color="black", scatter_kws={'marker':'o','linewidth':2}, line_kws={'linewidth':3, 'alpha':.6})
locs = array([ 0.8 , 0.9 , 1. ,  1.1,  1.2,  1.3,  1.4,  1.5,  1.6,  1.7])
plt.xticks(locs, size=18)
plt.yticks(size=18)
xlim(0.8, 1.7)

setp(ax1['whiskers'], color='black', linestyle='solid', linewidth=1, alpha=.5)
setp(ax1['caps'], color='black', linestyle='solid', linewidth=1, alpha=.5)
setp(ax1['boxes'], color='black', linewidth=2, alpha=.5)
setp(ax1['medians'], color='black', linewidth=2, alpha=.5)

plt.xlabel('PIB Index', fontsize=24, labelpad=15)
plt.ylabel('Linear Contrast Z score', fontsize=24)
plt.tick_params(direction='out', width=1)
plt.tight_layout()
#plt.annotate(r"$\beta$ = -1.89, p<0.05)", (0.8, 0.9), xycoords='axes fraction', fontsize=18)

sns.despine()   

#### PIB+ scatterplot ########
ax1 = sns.regplot("PIB_Index", "TaskPos", dat_pibpos, ci=False, truncate=True, 
    color="black", scatter_kws={'marker':'o','linewidth':2}, line_kws={'linewidth':3, 'alpha':.6})
sns.regplot("PIB_Index", "TaskPos", dat[dat.Group=="Old PIB+"], ci=False, fit_reg=False, scatter_kws={'marker':'o','linewidth':1, 'facecolors':'white','edgecolors':'black'}, ax=ax1)
xlim(0.8, 1.7)
plt.xlabel('PIB Index', fontsize=24, labelpad=15)
plt.ylabel('Linear Contrast Z score', fontsize=24)
plt.tick_params(direction='out', width=1)
plt.tight_layout()
sns.despine()   
plt.savefig(outfile, dpi=300) 





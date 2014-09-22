#!/usr/bin/env python
import sys, os
sys.path.append("/home/jagust/cindeem/CODE/PetProcessing/misc")
import rapid_art
import numpy as np

def CreateRegressors(outdir, art_output, num_vols):
    exists = False
    qa_file = os.path.join(outdir,'data_QA',art_output)
    outliers = np.loadtxt(qa_file, dtype=int)
    outliers = np.atleast_1d(outliers)
    if len(outliers) > 1:
        exists = True
        outlier_array = np.zeros((num_vols,len(outliers)),dtype=float)
        for i in range(len(outliers)):
            outlier_array[outliers[i],i]=1
        outfile = os.path.join(outdir, 'data_QA', 'outliers_for_fsl.txt')
        outlier_array.tofile(outfile)
        np.savetxt(outfile, outlier_array, fmt='%i', delimiter=u'\t')
        print 'Saved %s'%outfile
        return exists, outlier_array
    elif len(outliers) == 1:
        exists = True
        outlier_array = np.zeros((num_vols,len(outliers)),dtype=float)
        outlier_array[outliers[0],0] = 1
        outfile = os.path.join(outdir, 'data_QA', 'outliers_for_fsl.txt')
        outlier_array.tofile(outfile)
        np.savetxt(outfile, outlier_array, fmt='%i', delimiter=u'\t')
        print 'Saved %s'%outfile
        return exists, outlier_array
    else:
        outlier_array = np.array([])
        return exists, outlier_array


def CombineRegressors(mc_params, outlier_array):
    combined = np.hstack((mc_params, outlier_array))
    outfile = os.path.join(rundir, 'confound_regressors.txt')
    np.savetxt(outfile, combined, delimiter=u'\t')
    print 'Saved %s'%outfile
    return combined



if __name__ == '__main__':

    """
    Script to run rapid_art data QC from nipype. 
    
    Inputs:
    --------
    funcdatapath : Path to directory containing subject folders
    art_output : File to output list of outlier volumns
    rundir : Directory of each fMRI session
    infiles : Functional data file 
    param_file : FIle containing motion correction parameters
    param_source : 'FSL' or 'SPM' motion correction used to produce parameters?
    thresh : Threshold to determine motion and intensity outliers
    outdir : directory to output QA files
    
    """
    if len(sys.argv) ==1:
        print 'USAGE: python run_image_qa.py Bxx-xxx Bxx-xxx Bxx-xxx'
    else:
        args = sys.argv[1:]

    #Set up paths for current study
    ####################################################
    funcdatapath = '/home/jagust/DST/FSL/functional'
    art_output = 'art.filtered_func_data_outliers.txt'
    ####################################################

    for subj in args:
        subjdir = os.path.join(funcdatapath,subj)
        for run in os.listdir(subjdir):
            #Declare run-level paths and files
            ######################################################
            rundir = os.path.join(funcdatapath,subj,run)
            infiles = [os.path.join(rundir, 'Preproc.feat', 'filtered_func_data.nii.gz')]
            param_file = os.path.join(rundir, 'Preproc.feat', 'mc', 'prefiltered_func_data_mcf.par')
            param_source = 'FSL'
            thresh = 3
            outdir = rundir
            ######################################################
            if not rundir:
                continue
            else:
                #Run artdetect and create QA directory
                rapid_art.main(infiles, param_file, param_source, thresh, outdir)

                #Generate motion-intensity regressor for FSL and save in QA folder.
                #Combine motion-intensity regressors with motion correction parameters. 
                #Save combined confound regressors to run directory.
                mc_params = np.loadtxt(param_file)
                num_vols = len(mc_params)
                exists, outlier_array = CreateRegressors(outdir, art_output, num_vols)
                if exists:
                    confound_regressors = CombineRegressors(mc_params, outlier_array) 
                elif not exists:
                    outfile = os.path.join(rundir, 'confound_regressors.txt') 
                    np.savetxt(outfile, mc_params, delimiter=u'\t')
                    print 'Saved %s'%outfile
                

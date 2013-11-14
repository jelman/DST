#import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.spm as spm          # spm
import nipype.interfaces.utility as util     # utility
#import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model specification
import os, re                                   # system functions, regual expression
from glob import glob
from nipype.interfaces.base import Bunch
import json
import numpy as np
from nipype.interfaces.base import CommandLine

def save_json(filename, data):
    """Save data to a json file
    
    Parameters
    ----------
    filename : str
        Filename to save data in.
    data : dict
        Dictionary to save in json file.

    """
    fp = file(filename, 'w')
    json.dump(data, fp, sort_keys=True, indent=4)
    fp.close()


def load_json(filename):
    """Load data from a json file

    Parameters
    ----------
    filename : str
        Filename to load data from.

    Returns
    -------
    data : dict
   
    """
    fp = file(filename, 'r')
    data = json.load(fp)
    fp.close()
    return data


def get_names(subid, datadir, run = 1, type='Correct'):
    """lookinf in subjects directory in datadir
    finds folder of specified run  (eg run01)
    Finds any event files, based on type
    default type=Correct, (eg B*_Correct*.txt)
    returns list of filenames found"""
    globstr = os.path.join(datadir,subid,
                           'run%02d'%run,
                           'B*_%s*.txt'%type)
    result = glob(globstr)
    result.sort()
    return result

def parse_name(infile):
    """ pull out condition name from full filepath/filename"""
    _, base, _ = util.split_filename(infile)
    parts = base.split('_')
    name = ''.join(parts[-2:])
    return name
    

def generate_average_contrasts(info):
    """ read in a info bunch (for one run), generate contrasts appropriate
    for valid conditions"""
    outd = {}
    samples = util.np.arange(7)
    for i in samples:
        cond = [x for x in info.conditions if '%d'%i in x]
        outd[i] = cond
    all_cond = info.conditions
    final_contrasts = []
    for i in util.np.arange(7):
        if outd[i]:
            contrast_name =  '&'.join(outd[i])
            names = outd[i]
            indicies = []
            for n in names:
                indicies.append(all_cond.index(n))
            contrasts = util.np.zeros(len(all_cond))
            contrasts[util.np.asarray(indicies) ] = 1. / len(indicies)
            this_contrast = (contrast_name, 'T', all_cond, contrasts)
            final_contrasts.append(this_contrast)
            
    return final_contrasts


def get_info(event_files):
    """ generate a info Bunch to be used with model.SpecifySPMModel
    NOTE: only one for each run, create list tp pass to actual model"""
    
    conditions = []
    onsets = []
    durations = []
    
    for f in event_files:
        dat = util.np.loadtxt(f)
        if 'Lo' in f or 'Hi' in f:
            # do not include if 1 onset or less or higher level onsets
            continue
        try:
            onset = dat[:,0]
            dur = dat[:,1]
            name = parse_name(f)
            conditions.append(name)
            durations.append(dur.tolist())
            onsets.append(onset.tolist())
        except:
            print dat
    return [Bunch(conditions = conditions,
                  onsets = onsets,
                  durations = durations)]
    

def subjectinfo(subject_id, datadir):
    """ creates a Bunch object that holds
    conditions, onsets, durations
    given a subid, and associated datadir,
    implicitly reads two text files
    B*_Correct*.txt
    B*_Incorrect*.txt
    to get information to generate condisitons and onsets
    assumes fixed duration of 15
    """

    print "Subject ID: %s\n"%str(subject_id)
    output = []
    correct_globstr = os.path.join(datadir, 'B*_Correct*.txt')
    correct = glob(correct_globstr)
    incorrect_globstr = os.path.join(datadir, 'B*_Incorrect*.txt')
    incorrect = glob(correct_globstr)
    
    names = ['Task-Odd','Task-Even']
    for r in range(4):
        onsets = [range(15,240,60),range(45,240,60)]
        output.insert(r,
                      Bunch(conditions=names,
                            onsets=deepcopy(onsets),
                            durations=[[15] for s in names]))
    return output



def final_contrasts_json(contrast_list, outdir):
    """ given a list of contrasts
    generates a dictionary mapping
    contrast-name -> contrast number
    saves to json dict in outdir
    (so it can be grabbed for level2 to get correct
    contrst number -> contrast type, mapping)
    """
    newd = {}
    for val, con in enumerate(contrast_list):
        contrast_name = con[0]
        newd[contrast_name] = val + 1
    return newd
        

def get_subid(instr):
    """ pulls the subid Bxx-xxx out of a string
    returns text matching pattern"""
    m = re.search('B[0-9]{2}-[0-9]{3}', instr)
    try:
        return m.group()
    except:
        return None

def get_runs(indir):
    """given a subject dir
    glob for run directories
    sort and return
    """
    result = glob(os.path.join(indir, 'run*'))
    result.sort()
    return result

def get_run_asint(runs):
    """ given a list of run directories
    return run number
    """
    iruns = []
    for item in runs:
        _, nme = os.path.split(item)
        run_number = int(nme.strip('run'))
        iruns.append(run_number)
    return iruns

def make_dir(root, name = 'temp'):
    """ generate dirname string
    check if directory exists
    return exists, dir_string
    """
    outdir = os.path.join(root, name)
    exists = False
    if os.path.isdir(outdir):
        exists = True
    else:
        os.mkdir(outdir)
    return exists, outdir


def make_outlier_forspm(outliers):
    outlier_list = np.loadtxt(outliers, dtype = int)
    outlier_list = outlier_list.max(axis=1)
    pth, _ = os.path.split(outliers)
    newfile = os.path.join(pth, 'outliers_forspm.txt')
    outlier_list.tofile(newfile, sep='\n')
    return newfile

def spm_specify_model(info, movement, outliers, data4d, tr):

    # parse outliers file
    outlier_file = make_outlier_forspm(outliers)
    modelspec = model.SpecifySPMModel()
    modelspec.inputs.subject_info = info
    modelspec.inputs.outlier_files = outlier_file
    modelspec.realignment_parameters = movement
    modelspec.inputs.concatenate_runs        = False
    modelspec.inputs.input_units             = 'secs'
    modelspec.inputs.output_units            = 'secs'
    modelspec.inputs.functional_runs = data4d
    modelspec.inputs.time_repetition = tr
    modelspec.inputs.high_pass_filter_cutoff = 100
    out = modelspec.run()
    return out

def spm_level1(session_info,tr, mask):
    lvl1 = spm.Level1Design(matlab_cmd = 'matlab-spm8')
    lvl1.inputs.session_info = session_info
    lvl1.inputs.timing_units       = 'secs'
    lvl1.inputs.interscan_interval = tr
    lvl1.inputs.bases              = {'hrf':{'derivs': [1,0]}}
    lvl1.inputs.mask_image = mask
    out = lvl1.run()
    return out


def unzip(infile):
    gunzipfile, gz = os.path.splitext(infile)
    if not 'gz' in gz:
        #when running gunzip on file when
        return infile
    else:
       c3 = CommandLine('gunzip %s'%(infile))
       c3.run()
       return gunzipfile


if __name__ == '__main__':

    ## set up variables for  current study
    ############################################
    datadir = '/home/jagust/DST/FSL/functional'
    subject_glob = 'B*' 
    runs = [1] # make sure this is a list
    tr = 2.2
    ##################################################


    startdir = os.getcwd()
    # get all subjects
    allsub = glob(os.path.join(datadir, subject_glob))
    allsub.sort()
    # loop over subjects
    for sub_dir in allsub:
        subid = get_subid(sub_dir)
        if subid is None:
            print sub_dir, 'does not have a valid subid'
            continue
        print subid
        # get subject runs
        runs = get_runs(sub_dir)
        iruns = get_run_asint(runs)
        # loop over subject runs
        for run, rundir in zip(iruns, runs):
            # get files of events for given run
            types = ['Correct', 'Incorrect']
            event_files = []
            # find all event files given event types
            for t in types:
                tmp = get_names(subid, datadir, run=run, type = t)
                event_files += tmp

            # look for subject data
            globstr = os.path.join(datadir, subid, 'run%02d'%(run),
                                   'f.feat', 'filtered_func_data.nii.gz')
            # assume we found it otherwise raises exception
            run4d = glob(globstr)[0]
            
            ## movement parameters
            globstr =  os.path.join(datadir, subid, 'run%02d'%(run),
                                   'f.feat','mc','prefiltered_func_data_mcf.par')
            movement = glob(globstr)[0]
            ## mask
            globstr =  os.path.join(datadir, subid, 'run%02d'%(run),
                                    'f.feat','mask.nii*')
            mask = glob(globstr)
            mask.sort()
            mask = mask[0]
            mask = unzip(mask)

            ## outlier files
            globstr = os.path.join(rundir, 'motion_outliers.txt')
            outliers = glob(globstr)[0]

            # get run information from event files
            info = get_info(event_files)

            # need contrasts based on good conditions
            final_contrasts = generate_average_contrasts(info[0])
            con_dict = final_contrasts_json(final_contrasts, None)
            # make the level 1 directory
            
            model_out = spm_specify_model(info, movement, outliers, run4d, tr)
            session_info = model_out.outputs.session_info
            # generate the model.SpecifySPMModel
            # Link into pipeline and  iterate properly over subjects, runs
            # Specify higher level model
            
            exists, lvl1_dir = make_dir(rundir, name = 'spm_level1' )
            if exists:
                print lvl1_dir, 'exists, remove to re-run'
                continue
            os.chdir(lvl1_dir)
            lvl1_out = spm_level1(session_info,tr, mask)
            if not lvl1_out.runttime.returncode == 0:
                print lvl1_out.runtime.stderr
                os.chdir(startdir)
                continue
            ###  TO DO
            ## split 4drun into 3d (or set flag??)
            ## implement estimate contrast
            

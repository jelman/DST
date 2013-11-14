#!/usr/bin/env python
import pandas
import os
import numpy as np
import sys


def SaveOutfile(subj,frame, filename, pth='/home/jagust/DST/BehavioralData'):
        outfile = os.path.join(pth, subj, filename)
        frame.to_csv(outfile, index=False)
        print 'Saved %s'%outfile

def split_subid(insubid):
    """ splits year off subid
    eg B12-895 -> 895
    """
    head, tail = insubid.split('-') # only look at end of subid
    return tail

def get_retrieval_filename(subid, pth='/home/jagust/DST/BehavioralData'):
    """ Given subject ID and behavioral data path, 
    (default pth = /home/jagust/DST/BehavioralData)
    return subjects tab delimited behavioral txt file"""
    subjdir = os.path.join(pth,subid)
    smallid = split_subid(subid)
    file_name = 'DST_Test-' + smallid + '-1_retrieval.txt'
    infile = os.path.join(subjdir, file_name)
    if not os.path.isfile(infile):
        print '%s is not found'%infile
        return None
    else:
        return infile

def load_retrieval(behavioral_file):
    frame = pandas.read_csv(behavioral_file, sep='\t')
    newdat = frame.reindex(columns = retrieval_cols)
    mask = [isinstance(x,str) for x in newdat.NewCode]
    maskdat = newdat[mask]
    testmask = [("New" in x) or ("NEW" in x) for x in maskdat.NewCode]
    finaldat = maskdat[testmask]
    return finaldat

def get_behavioral(subid, run, filename, pth='/home/jagust/DST/BehavioralData'):
    """ Given subject ID and behavioral data path, 
    (default pth = /home/jagust/DST/BehavioralData)
    return subjects tab delimited behavioral ttxt file"""
    subjdir = os.path.join(pth,subid)
    rundir = os.path.join(subjdir, run)
    infile = os.path.join(rundir, filename)
    if not os.path.isfile(infile):
        print '%s is not found'%infile
        return None
    else:
        return infile

def get_tr_info(subid, run, rtfile):
            infile = get_behavioral(subid, run, rtfile)
            rtdat = np.loadtxt(infile)
            trs = np.count_nonzero(rtdat[5:9]==1.)
            onset_adjust = trs * 2.2
            return onset_adjust

def CalcConf(resp):
    if (resp == 1 or resp == 4):
        return 'Hi'
    elif (resp == 2 or resp == 3):
        return 'Lo'
    else:
        return ''

def CalcOldNew(code):
    if "NEW" in code:
        return 'old'
    elif "New" in code:
        return 'new'


if __name__ == '__main__':

    if len(sys.argv) ==1:
        print 'USAGE: python parse_behavioral.py Bxx-xxx Bxx-xxx Bxx-xxx'
    else:
        args = sys.argv[1:]


    ############ Setup variables for current study #####
    ####################################################
    #Set Behavioral and functional data paths
    behavdatapath = '/home/jagust/DST/BehavioralData'
    funcdatapath = '/home/jagust/DST/FSL/functional'
    runs = ['session_encode1','session_encode2','session_encode3']
    #Set stimulus duration and weight
    duration = 6.6
    weight = 1
    ## Define columns of interest
    retrieval_cols = ['Subject', 'NewCode','GistSlide.ACC','DetailSlide.ACC',
                        'GistSlide.RESP','OldNew']
    encode_cols = ['Onset', 'Image','ACC','RT']
    merged_data_cols = ['Subject','Run','NewCode','Onset','Duration',
                        'Weight','RT','ACC','GistSlide.ACC','DetailSlide.ACC',
                        'GistSlide.RESP','Confidence','OldNew']
    ##File names
    rtfile = 'scenedisplist.txt'
    encodefile = 'parsed_runstats.csv'
    ####################################################
    ####################################################

    for subj in args:
    ##Load and transform retrieval data    
        retrieval_file = get_retrieval_filename(subj)
        if retrieval_file is None:
            print 'Retrieval file not created for %s'%subj
            continue
        retrievaldat = load_retrieval(retrieval_file)
        retrievaldat = retrievaldat.reset_index(drop=True)
        retrievaldat['Subject'] = subj
        retrievaldat['OldNew'] = [CalcOldNew(code) for code in retrievaldat['NewCode']]
        retrievalgrp = retrievaldat.groupby(['Subject','NewCode','OldNew'], as_index=False)
        retrievalsum = retrievalgrp.sum()
        retrievalout = subj + '_RetrievalPerformance.csv'
        SaveOutfile(subj,retrievalsum, retrievalout)

        ##Load and transform encoding data
        encodeframe = pandas.DataFrame()
        for run in runs:
            infile = get_behavioral(subj, run, encodefile)
            encodedata = np.genfromtxt(infile,delimiter=',',dtype=None)
            frame = pandas.DataFrame.from_records(encodedata)
            newframe = pandas.DataFrame(frame)
            newframe.columns = encode_cols
            newframe['Subject'] = subj
            newframe['Run'] = run
            encodeframe = encodeframe.append(newframe, ignore_index=True)
            encodeframe['Run'] = [x.replace("session_encode","run0") for x in encodeframe['Run']]
        encodeframe['Image'] = ['../' + x for x in encodeframe['Image']]        
        encodeframe = encodeframe.sort_index(by=['Run','Onset'])

        ##Load NewCode-Image pairing file.
        ##Merge NewCode-Image file to encoding data, then retrieval  to combined data.
        newcode_file = os.path.join(behavdatapath,'NewCodeList.txt')
        newcodelist = pandas.read_csv(newcode_file, sep='\t')
        encode_merge = pandas.merge(encodeframe,newcodelist,how='left')
        enc_ret_merge = pandas.merge(encode_merge, retrievalsum, how='left')
        enc_ret_merge['Confidence'] = [CalcConf(resp) for resp in enc_ret_merge['GistSlide.RESP']]
        noresp = enc_ret_merge['ACC']=='NA'
        enc_ret_merge['RT'] = enc_ret_merge['RT'].astype(float)
        enc_ret_merge['RT'][noresp] = np.nan        
        full_data = pandas.DataFrame(enc_ret_merge, columns=merged_data_cols)
        full_data['Duration'] = duration
        full_data['Weight'] = weight
        full_data['Weight'] = full_data['Weight'].astype(int)
        full_data = full_data.sort_index(by=['Run','Onset'])
        dataout = subj + '_Data.csv'
        SaveOutfile(subj,full_data, dataout)

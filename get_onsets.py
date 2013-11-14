#!/usr/bin/env python
import sys, os
import numpy as np
import argparse


def onsets_from_files(ttl, scenelist):
    """ using timestamps in ttl file and specification of 
    onsets (value == 2, representing new image display)
    generate a list of onset times"""
    
    # parse ttl file to get timestamps
    ttl_time = []
    for line in open(ttl):
        parts = line.split('\t')
        if len(parts) == 4 and 'scan' in line:
            ttl_time.append(parts[0])
    ttl_time = np.array(ttl_time).astype(long)
    # get scene list
    scene_list = np.loadtxt(scenelist)
    if not scene_list.shape == ttl_time.shape:
        raise IndexError('shape mismatch scene = %s; ttl = %s'%(scene_list.shape, 
                                                                ttl_time.shape))
    onsets = ttl_time[scene_list == 2]
    pth, _ = os.path.split(ttl)
    newfile = os.path.join(pth, 'onsets.txt')
    onsets.tofile(newfile, sep='\n')
    print 'wrote %s'%newfile


if __name__ == '__main__':

    print 'get onsets'
    # create the parser
    parser = argparse.ArgumentParser(
        description='Get timestamps for onsets ')

    # add the arguments

    parser.add_argument(
        '-ttl', dest='ttl', default=None,
        help='specify ttl.log file')

    parser.add_argument(
        '-scenedisplist', dest='scenelist', default=None,
        help='specify scenedisplist.txt')
        
    if len(sys.argv) ==1:
        parser.print_help()
    else:
        args = parser.parse_args()
        onsets_from_files(args.ttl, args.scenelist)
    
    

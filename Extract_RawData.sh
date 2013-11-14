#!/bin/sh
#Set up subjects folders and data for processing
# Command line arguments: <subject number>

#Verify command line arguments have been given
if [ $# -eq 0 ]; then
	echo "Usage: $0 <subject number>"
	exit 0
fi

while [ "$1" ]
do

###Declare folder variables, these should be modified per study
    study=/home/jagust/DST/FSL
    rawdir=/home/jagust/DST/RawData
    subj=$1

    for run in T1 dark_fluid run01 run02 run03;
    do
        tar --strip-components=3 -zxvf "$rawdir"/"$subj"/"$run"/*.tgz -C "$rawdir"/"$subj"/"$run"/ tmp/tmp*/renamed
        rm "$rawdir"/"$subj"/"$run"/*.tgz
    done

    

    shift 1
done

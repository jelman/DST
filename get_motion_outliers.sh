#!/bin/sh
#Runs the command fsl_motion_outliers for all runs on specified subjects.
#Saves out motion_outliers.txt to each run folder.

if [ $# -eq 0 ]; then
	echo "Runs the command fsl_motion_outliers for all runs on specified subjects."	
	echo "Saves out motion_outliers.txt to each run folder."	
	echo "Usage: $0 <subject number>"
	exit 0
fi

while [ "$1" ]
do

subj=$1

    for run in run01 run02 run03 
    do

    fsl_motion_outliers -i /home/jagust/DST/FSL/functional/$subj/$run/f.nii.gz -o /home/jagust/DST/FSL/functional/$subj/$run/motion_outliers.txt --dummy=5 -s /home/jagust/DST/FSL/functional/$subj/$run/outlier_metric_values.txt -p /home/jagust/DST/FSL/functional/$subj/$run/outlier_metric_plot.png

    done

shift 1

done

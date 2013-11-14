#!/bin/sh
#Runs FLIRT in order to obtain transformation matrix 
#registering initial_highres to highres. Copies over to 
#reg folder in feat directory and runs updatefeatreg
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
    funcdir=/home/jagust/DST/FSL/functional
    strucdir=/home/jagust/DST/FSL/structural
    subj=$1

    flirt -cost mutualinfo -in $strucdir/$subj/dark_fluid_brain.nii.gz -ref $strucdir/$subj/T1_brain.nii.gz -out $strucdir/$subj/dark_fluid_reg -omat $strucdir/$subj/initial_highres2highres.mat -dof 6

    cp $strucdir/$subj/initial_highres2highres.mat $funcdir/$subj/run01/Detail.feat/reg/ -f
    cp $strucdir/$subj/initial_highres2highres.mat $funcdir/$subj/run02/Detail.feat/reg/ -f
    cp $strucdir/$subj/initial_highres2highres.mat $funcdir/$subj/run03/Detail.feat/reg/ -f
    cp $strucdir/$subj/initial_highres2highres.mat $funcdir/$subj/run01/Gist.feat/reg/ -f
    cp $strucdir/$subj/initial_highres2highres.mat $funcdir/$subj/run02/Gist.feat/reg/ -f
    cp $strucdir/$subj/initial_highres2highres.mat $funcdir/$subj/run03/Gist.feat/reg/ -f

    updatefeatreg $funcdir/$subj/run01/Detail.feat
    updatefeatreg $funcdir/$subj/run02/Detail.feat
    updatefeatreg $funcdir/$subj/run03/Detail.feat
    updatefeatreg $funcdir/$subj/run01/Gist.feat
    updatefeatreg $funcdir/$subj/run02/Gist.feat
    updatefeatreg $funcdir/$subj/run03/Gist.feat

shift 1
done

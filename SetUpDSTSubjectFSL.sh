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
funcdir=/home/jagust/DST/FSL/functional
strucdir=/home/jagust/DST/FSL/structural
rawdir=/home/jagust/DST/RawData
subj=$1


###Set subject folders. Modify run labels per study

	mkdir $funcdir/$subj
	mkdir $funcdir/$subj/run01
	mkdir $funcdir/$subj/run02
	mkdir $funcdir/$subj/run03
	mkdir $strucdir/$subj

#Import dicoms.
###Verify folder names of dicom data. This will depend on sequence name and run number
	dcm2nii -o $funcdir/$subj/run01/ -i Y -d N -p N -e N $rawdir/$subj/run01
	dcm2nii -o $funcdir/$subj/run02/ -i Y -d N -p N -e N $rawdir/$subj/run02
	dcm2nii -o $funcdir/$subj/run03/ -i Y -d N -p N -e N $rawdir/$subj/run03
	dcm2nii -o $strucdir/$subj/ -i Y -d N -e N $rawdir/$subj/T1
	dcm2nii -o $strucdir/$subj/ -i Y -d N -e N $rawdir/$subj/dark_fluid


#Rename and reorient functional files
	for imported_nii in `find $funcdir/$subj -name "*_ep2d_2_2TR_axial_*.nii.gz"`
	    do
	    imported_nii_dir="${imported_nii%/*_ep2d*.nii.gz}"
	    mv $imported_nii $imported_nii_dir/f.nii.gz
	done

#Rename and reorient structural files
	for imported_nii in `find $strucdir/$subj -name "B*t1_mpr_tra*.nii.gz"`
	    do
	    imported_nii_dir="${imported_nii%/*t1_mpr_tra*.nii.gz}"
	    mv $imported_nii $imported_nii_dir/"T1.nii.gz"
	done

	for imported_nii in `find $strucdir/$subj -name "*t1_tirm_tra*.nii.gz"` 
	    do
	    imported_nii_dir="${imported_nii%/*t1_tirm_tra*.nii.gz}"
	    mv $imported_nii $imported_nii_dir/"dark_fluid.nii.gz"
	    done

#Run BET on structural scans
   bet $strucdir/$subj/T1.nii.gz $strucdir/$subj/T1_brain.nii.gz -f .3
   bet $strucdir/$subj/dark_fluid.nii.gz $strucdir/$subj/dark_fluid_brain.nii.gz -f .4

shift 1
done

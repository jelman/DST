#!/bin/sh

for i in /home/jagust/DST/FSL/functional/2ndLevel/Details/B*.gfeat/cope1.feat/featquery_CorrIncorr_RightLOC/report.txt
    do
    awk '{ print $9 }' $i | tr -s '\n' '\t'
    echo " "

done

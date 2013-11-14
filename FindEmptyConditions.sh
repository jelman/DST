#!/bin/sh

#Removes all empty condition onset files and logs in EmptyConditions.txt

for file in `find /home/jagust/DST/FSL/functional/B*/run*/ -name "B*_run*.txt"`; do

    if [ ! -s $file ]; then
        echo $file >> /home/jagust/DST/BehavioralData/EmptyConditions.txt
        rm $file
    fi
done
 	

#! /bin/bash

set -x
echo " Setting near-sync off for PD creation"

for c in {61..120}
do
ncli pd clear-schedules name=nsy1pd$c
ncli pd rm-snap name=nsy1pd$c clear-all=true
ncli pd rm name=nsy1pd$c
done 

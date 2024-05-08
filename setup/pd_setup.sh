#! /bin/bash

set -x
#echo " Setting near-sync off for PD creation"

for c in {1..40}
do
ncli pd clear-schedules name=f1pd$c
ncli pd rm-snapshot name=f1pd$c clear-all=true
ncli pd rm name=f1pd$c
##ncli pd create name=logan1pd$c
#sleep 1
##ncli pd protect name=logan1pd$c vm-names=uptime_aes_logan_$c
##ncli pd add-hourly-schedule local-retention=1 name=logan1pd$c start-time="09/14/2018 16:30:00 PST"
#ncli pd add-hourly-schedule local-retention=6 remote-retention=luigi11:6 name=g1pd$i start-time="02/14/2018 16:30:00 PST"
#ncli pd rm-snapshot name=b1pd$c clear-all=true
done 

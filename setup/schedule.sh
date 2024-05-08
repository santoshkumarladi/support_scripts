#! /bin/bash

set -x
echo " Adding schedule"
for i in {1..60}
do
#sleep 2
#ncli pd add-minutely-schedule local-retention-type=WEEKS remote-retention-type=falcon:WEEKS every-nth-minute=1 local-retention=1 remote-retention=falcon:1 name=nsb1pd$i
#ncli pd add-hourly-schedule local-retention=6 name=g1pd$i
ncli pd clear-schedules name=g1pd$i
#ncli pd add-hourly-schedule local-retention=6 remote-retention=luigi11:6 name=g1pd$i start-time="02/14/2018 16:30:00 PST"
#ncli pd add-hourly-schedule local-retention=6 remote-retention=falcon:6 name=b1pd$i
done

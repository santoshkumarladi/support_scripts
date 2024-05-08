#! /bin/bash

set -x
echo " Setting near-sync off for PD creation"


for i in {1..6}
do
ncli pd create name=nsbpd$i
done
#for pd_name in {1..6}
#do
#vm_name = $pd_name * 10

for c in {1..10}
do
ncli pd protect name=nsbpd1 vm-names=centos_b_pd_$c
done
for c in {10..20}
do
ncli pd protect name=nsbpd2 vm-names=centos_b_pd_$c
done
for c in {20..30}
do
ncli pd protect name=nsbpd3 vm-names=centos_b_pd_$c
done
for c in {30..40}
do
ncli pd protect name=nsbpd4 vm-names=centos_b_pd_$c
done
for c in {40..50}
do
ncli pd protect name=nsbpd5 vm-names=centos_b_pd_$c
done
for c in {50..60}
do
ncli pd protect name=nsbpd6 vm-names=centos_b_pd_$c
done

sleep 600

for i in {1..6}
do 
ncli pd add-minutely-schedule local-retention-type=WEEKS remote-retention-type=WEEKS every-nth-minute=1 local-retention=1 remote-retention=falcon:1 name=nsbpd$i
done
#done 

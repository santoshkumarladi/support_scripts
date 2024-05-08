#! /bin/bash

set -x
while [ 1 ]
do
append1=`date`
#append1=`date +%Y%m%d%H%M%S`
echo $appendi1
for ip in `svmips`; do echo $ip; ssh -q $ip "curl http://0:2009/h/gflags?v=3";done;
sleep 600 
append2=`date`
echo $appendi1
for ip in `svmips`; do echo $ip; ssh -q $ip "curl http://0:2009/h/gflags?v=0";done;
sleep 1200
done

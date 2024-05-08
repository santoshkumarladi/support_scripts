#! /bin/bash

set -x
while [ 1 ]
do
for ip in `svmips`; do echo $ip; ssh -q $ip "curl http://0:2009/h/gflags?stargate_aes_enabled=false";done;
sleep 600 
for ip in `svmips`; do echo $ip; ssh -q $ip "curl http://0:2009/h/gflags?stargate_aes_enabled=true";done;
sleep 600
done

#! /bin/bash
#while [ 1 ]
#do
set -x
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo rm -rf  ~/data/cores/*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/*FATAL*";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/stargate*.ou*";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/cerebro*.ou*";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/curator*.ou*";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/cassa*.ou*";done;
#sleep 600
#done
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo service iptables stop";done;
#sleep 1
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.16.20:/volume1/binlog/ /mnt/archive";done;

#! /bin/bash
#while [ 1 ]
#do
set -x
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf  ~/data/cores/z*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf  ~/data/cores/h*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf  ~/data/cores/p*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf  ~/data/cores/a*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf  ~/data/cores/m*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf  ~/data/cores/n*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf  ~/data/cores/i*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf  ~/data/cores/d*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/z*FATAL*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/h*FATAL*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/p*FATAL*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/a*FATAL*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/m*FATAL*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/n*FATAL*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/i*FATAL*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo rm -rf ~/data/logs/d*FATAL*";done;
#sleep 600
#done
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo service iptables stop";done;
#sleep 1
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.16.20:/volume1/binlog/ /mnt/archive";done;

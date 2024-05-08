#! /bin/bash


set -x
while [ 1 ]
do
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo rm -rf ~/data/logs/zoo*INFO*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo rm -rf ~/data/logs/zoo*WARNING*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo rm -rf ~/data/cores/a*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo rm -rf ~/data/cores/nu*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo rm -rf ~/data/cores/in*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo rm -rf ~/data/cores/pi*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo rm -rf ~/data/cores/zoo*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo rm -rf ~/data/binary_logs/*';done;
sleep 60
done
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo service iptables stop";done;
#sleep 1
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.16.20:/volume1/binlog/ /mnt/archive";done;

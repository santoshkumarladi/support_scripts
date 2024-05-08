#! /bin/bash

set -x
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/9XG38LZS/cores';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/9XG38LZS/binary_logs';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/9XG38KXY/cores';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/9XG38KXY/binary_logs';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/PN2334PBGTZ02T/cores';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/PN2334PBGTZ02T/binary_logs';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/PN2334PBGK821T/cores';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/PN2334PBGK821T/binary_logs';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/PN1334PBHR7EZP/cores';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/PN1334PBHR7EZP/binary_logs';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/PN1334PBHRRWBP/cores';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'mkdir /home/nutanix/data/stargate-storage/disks/PN1334PBHRRWBP/binary_logs';done;

#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo service iptables stop";done;
#sleep 1
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.16.20:/volume1/binlog/ /mnt/archive";done;

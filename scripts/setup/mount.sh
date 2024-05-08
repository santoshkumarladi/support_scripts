#! /bin/bash

set -x
ncli cluster add-to-name-servers servers=10.40.64.15,10.40.64.16
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo yum install -y nfs-utils --nogpgcheck";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mkdir /mnt/archive";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.40.167.227:/temp_logs /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.40.231.225:/temp_logs /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount -o vers=3 10.40.167.231:/volume3 /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.40.167.227:/volume2 /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.15.82.31:/volume1 /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.15.82.117:/volume3 /mnt/archive";done;
#10.5.66.69
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount -o vers=3 10.40.167.228:/volume2 /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.40.231.198:/volume2 /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "cp /home/nutanix/sys_stats_collector.py /home/nutanix/bin/";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.15.81.55:/volume1/binlog/Manual_Logs /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.15.88.23:/volume1/binlog/Manual_Logs /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.67.114:/volume2/binlog/Manual_Logs /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.67.114:/volume1/binlog/Manual_Logs /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.67.106:/volume1/binlog/Manual_Logs /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.67.106:/volume2/binlog/Manual_Logs /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.67.106:/volume2/binlog/Manual_Logs /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.74.109:/volume1/Manual_Logs /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.16.20:/volume2/bugs/ /mnt/archive";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "/usr/local/nutanix/cluster/bin/genesis stop sys_stat_collector";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "/usr/local/nutanix/cluster/bin/cluster start";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo service iptables stop";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "ls -d /mnt/archive/logan*";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep "^F0320" ~/data/logs/*.FATAL.*';done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "ls -ltr ~/data/cores | tail -n 10";done;

#sleep 1
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.16.20:/volume1/binlog/ /mnt/archive";done;

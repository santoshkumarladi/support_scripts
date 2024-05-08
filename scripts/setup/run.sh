#! /bin/bash

set -x
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep "^F0*" ~/data/logs/*.FATAL.* | grep -v QFATAL ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip "ls -ltr ~/data/cores";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip "ls -ltr ~/data/cores | tail -n 10";done;
#for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep AddressSanitizer ~/data/logs/stargate.out*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep kControlBlockKey ~/data/logs/stargate*ERR* ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep SIG ~/data/logs/stargate.out* | grep -v SIGA';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep SIG ~/data/logs/cerebro.out* | grep -v SIGA';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep SIG ~/data/logs/curator.out* | grep -v SIGA';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep SIG ~/data/logs/cassandra.out* | grep -v SIGA';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -i Fatal ~/data/logs/cassandra.out* | grep -v QFATAL ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep "Marking AES extent group" ~/data/logs/sta*ERROR* ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -i "retr.* corrupt egroup" ~/data/logs/sta*INFO* ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep kSliceChecksumMismatch ~/data/logs/sta*ERROR* ';done;
#for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -i Deadlock ~/data/logs/cassandra.out*  ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep WARN ~/data/logs/aesdb/* | grep -v STAT | grep -v db_impl.cc:441 | grep -v db_impl.cc:445 | grep -v db_impl.cc:449';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo df -lh | grep md2';done;

for ip in `svmips`; do echo $ip; ssh -q $ip "sudo service iptables stop";done;
sleep 1
#for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.5.16.20:/volume1/binlog/ /mnt/archive";done;

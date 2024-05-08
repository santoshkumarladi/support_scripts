#! /bin/bash

set -x
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -a "^F0*" ~/data/logs/*.FATAL.* | grep -v QFATAL ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip "ls -ltr ~/data/cores | tail -n 10";done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -a SIG ~/data/logs/stargate.out*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -a kControlBlockKey ~/data/logs/stargate*ERR* ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -a SIG ~/data/logs/curator.out*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -a SIG ~/data/logs/cassandra.out*';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -ia Fatal ~/data/logs/cassandra.out* | grep -v QFATAL ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -a "Marking AES extent group" ~/data/logs/sta*ERROR* ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -a kSliceChecksumMismatch ~/data/logs/sta*ERROR* ';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -ia corrupt ~/data/logs/cassandra.out* | grep -v false | grep -v counters_recovery_op.cc';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo zgrep -a WARN ~/data/logs/aesdb/* | grep -v STAT | grep -v db_impl.cc:441 | grep -v db_impl.cc:445';done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'sudo df -lh | grep md2';done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo service iptables stop";done;

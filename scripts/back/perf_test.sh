#! /bin/bash

set -x
sudo mount 10.40.231.199:/volume1 -o vers=3 /var/www/html/TEST_LOGS
sleep 3
mkdir /var/www/html/TEST_LOGS/perf_test
sleep 3
#/opt/iozone/bin/iozone -R -i 0 -i 1 -i 2 -s 1g -r 4k -t 1 -F /var/www/html/TEST_LOGS/perf_test/perf_test1
#/opt/iozone/bin/iozone -R -i 0 -i 1 -i 2 -s 1g -r 8k -t 1 -F /var/www/html/TEST_LOGS/perf_test/perf_test1
#/opt/iozone/bin/iozone -R -i 0 -i 1 -i 2 -s 1g -r 1m -t 1 -F /var/www/html/TEST_LOGS/perf_test/perf_test1
day=`date`
echo "Date: $day" 
echo "-----------------------------------------------------"
echo "-----------------------------------------------------"
echo "-----------------------------------------------------" 
/opt/iozone/bin/iozone -a -R -i 0 -i 1 -i 2 -s 1g -f /var/www/html/TEST_LOGS/perf_test/perf_test1
echo "-----------------------------------------------------"
echo "-----------------------------------------------------"
echo "-----------------------------------------------------" 
#/opt/iozone/bin/iozone -a -R -i 0 -i 1 -i 2 -s 1g -f /var/www/html/TEST_LOGS/perf_test/perf_test1 

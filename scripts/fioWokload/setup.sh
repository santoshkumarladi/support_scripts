#!/bin/bash
sleep 120
#file="/home/nutanix/FioWorkload.py"
#if [ -f "$file" ]
#then
        echo "Deleting file "
        rm -rf /home/nutanix/FioWorkload.py
        wget http://10.4.16.50/home/shivayogi.davanageri/FioWorkload.py -P /home/nutanix/
#else
#       wget http://10.4.16.50/home/shivayogi.davanageri/FioWorkload.py -P /home/nutanix/
#fi
sleep 30
file="/home/nutanix/FioWorkload.py"
if [ -f "$file" ]
then
        python /home/nutanix/FioWorkload.py > /home/nutanix/fio_sdb.logs 2>&1 &
else
        python /home/nutanix/FioWorkload_bk.py > /home/nutanix/fio_sdb_bk.logs 2>&1 &
fi

#!/bin/bash
#sleep 120
        echo "Deleting file "
        sudo rm -rf /home/nutanix/stressLargeVm.py
        sudo rm -rf /home/nutanix/log_fio
        sudo rm -rf /home/nutanix/run_fio.sh
        sudo rm -rf /home/nutanix/run_dd.sh
        sudo rm -rf /home/nutanix/*.state
        sudo rm -rf /home/nutanix/local*
        sudo rm -rf /home/nutanix/stressFio.py
        wget http://10.41.70.50/scripts/run_fio.sh -P /home/nutanix/
        wget http://10.41.70.50/scripts/stressFio.py -P /home/nutanix/
        wget http://10.41.70.50/scripts/stressLargeVm.py -P /home/nutanix/
        sudo chmod 777 /home/nutanix/stressLargeVm.py
        wget http://10.41.70.50/scripts/run_dd.sh -P /home/nutanix/
        sudo chmod 777 /home/nutanix/run_dd.sh
sleep 30
file="/home/nutanix/stressFio.py"
if [ -f "$file" ]
then
        python /home/nutanix/stressLargeVm.py > /home/nutanix/fio_sdb.logs 2>&1 &
else
        python /home/nutanix/stressLargeVm.py > /home/nutanix/fio_sdb_bk.logs 2>&1 &
fi

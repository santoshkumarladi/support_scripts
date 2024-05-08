#! /bin/bash

set -x
while [ 1 ]
do
python /home/nutanix/diagnostics/checkpoint_stargate_disk_wal.py --zeus_disk_id=53 
python /home/nutanix/diagnostics/checkpoint_stargate_disk_wal.py --zeus_disk_id=54 
python /home/nutanix/diagnostics/checkpoint_stargate_disk_wal.py --zeus_disk_id=55 
sleep 60 
done

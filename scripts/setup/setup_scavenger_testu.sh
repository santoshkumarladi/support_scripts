#! /bin/bash


disk_serial_name=$1
disk_device_name=$2


echo "Setting up scavenger archive disk for disk with serial name $disk_serial_name"
echo "Step 1: Deleting /home/nutanix/cores and /home/nutanix/binary_logs directory"
rm -rf ~/data/cores
rm -rf ~/data/binary_logs

echo "Step 2: Set planned usage"
commandline=$(disk_operator set_planned_outage $disk_serial_name)
echo $commandline

echo "Step 3: Marking disk unusable"
commandline=$(disk_operator mark_disks_unusable $disk_device_name)
echo $commandline

echo "Step 4: Creating archive_dir, cores, binary_logs directories"
commandline=$(mkdir /home/nutanix/data/stargate-storage/disks/$disk_serial_name/archive_dir)
echo $commandline
commandline=$(mkdir /home/nutanix/data/stargate-storage/disks/$disk_serial_name/cores)
echo $commandline
commandline=$(mkdir /home/nutanix/data/stargate-storage/disks/$disk_serial_name/binary_logs)
echo $commandline

echo "Step 5: Creating symlinks"
commandline=$(ln -s /home/nutanix/data/stargate-storage/disks/$disk_serial_name/cores ~/data/cores)
echo $commandline
commandline=$(ln -s /home/nutanix/data/stargate-storage/disks/$disk_serial_name/binary_logs ~/data/binary_logs)
echo $commandline

echo "Step 6: Creating scavenger gflags file"
echo "--archive_url=local:///home/nutanix/data/stargate-storage/disks/$disk_serial_name/archive_dir" > /home/nutanix/config/scavenger.gflags
echo "--timeout_secs=3600" >> /home/nutanix/config/scavenger.gflags

echo "Step 7: Restarting Scavenger service"
commandline=$(/usr/local/nutanix/cluster/bin/genesis stop scavenger; /usr/local/nutanix/cluster/bin/genesis restart)
echo $commandline

echo "Done"

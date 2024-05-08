#
# Copyright (c) 2013 Nutanix Inc. All rights reserved.
#
# Author: rohit@nutanix.com
#
# $1 = number of disks
# $2 = runtime in seconds
# $3 = num outstanding
# $4 = block size
# $5 = zfs/ext4 (optional)

# Disk names and the ioengine depend on the hypervisor hosting the uvms.
io_engine="libaio"
for file_prefix in vd xvd sd; do
  test -b "/dev/${file_prefix}b" && break
done

UNAME=`uname`
if [[ $UNAME == Linux* ]]; then
  disk_list=`python -c "
disk_list=[]
for ii in range($1):
  disk_list.append(\"/dev/$file_prefix%s\"%chr(ord(\"b\")+ii))
print \":\".join(disk_list)"`
elif [[ $UNAME == CYGWIN* ]]; then
  io_engine="windowsaio"
  disk_list='\\.\PhysicalDrive1'
  for i in `seq $1`; do if [ $i -ne 1 ]
  then disk_list=$disk_list':\\.\PhysicalDrive'$i; fi; done
else
  echo "Unknown UVM OS"
  exit -1
fi

direct=1
if [[ "$5" = "zfs" ]]; then
  disk_list=/zfs/file_for_read_test
  direct=0 # zfs does not support O_DIRECT, use sync ioengine instead
  io_engine=sync
fi
if [[ "$5" = "ext4" ]]; then
  disk_list=/mnt/perf_dir/file_for_test
  direct=0 # zfs does not support O_DIRECT, use sync ioengine instead
  io_engine=sync
fi

fio_log_prefix="/home/nutanix/fio_logs/fio_log"

jobs=$(nproc)
iodepth=$(($3/$jobs))
if [ $iodepth -eq 0 ]; then
  jobs=1
  iodepth=$3
fi

sudo /usr/bin/fio --write_bw_log=$fio_log_prefix --write_iops_log=$fio_log_prefix --write_lat_log=$fio_log_prefix --log_avg_msec=1000 --filename=$disk_list --direct=$direct --rw=randread --bs=$4 --iodepth=$iodepth --runtime=$2 --time_based --group_reporting --name=file1 --ioengine=$io_engine --numjobs=$jobs

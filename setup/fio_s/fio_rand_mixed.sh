#
# Copyright (c) 2013 Nutanix Inc. All rights reserved.
#
# Author: rohit@nutanix.com
#
# $1 = number of disks
# $2 = runtime in seconds
# $3 = num outstanding per thread
# $4 = block size
# $5 = %reads
# $6 = %writes
# $7 = time based (optional)
# $8 = zfs or ext4 (optional)

# Check total percent is 100
if [ $(($5 + $6)) -ne 100 ]; then
  echo "Read + Write percent should be equal to 100"
  exit -1
fi

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

if [ "$7" = "true" ]; then
  time_based="--time_based"
else
  time_based=""
fi

direct=1
if [[ "$7" = "zfs" || "$8" = "zfs" ]]; then
  disk_list=/zfs/file_for_$0_test
  direct=0 # zfs does not support O_DIRECT, use sync ioengine instead
  io_engine=sync
fi
if [[ "$7" = "ext4" || "$8" = "ext4" ]]; then
  disk_list=/mnt/perf_dir/file_for_test
  direct=0 # zfs does not support O_DIRECT, use sync ioengine instead
  io_engine=sync
fi

jobs=$(nproc)
iodepth=$(($3/$jobs))
if [ $iodepth -eq 0 ]; then
  jobs=1
  iodepth=$3
fi

sudo /usr/bin/fio --filename=$disk_list --direct=$direct --rw=randrw --bs=$4 --iodepth=$iodepth --runtime=$2 --group_reporting --name=file1 --ioengine=$io_engine --rwmixread=$5 --rwmixwrite=$6 $time_based --numjobs=$jobs

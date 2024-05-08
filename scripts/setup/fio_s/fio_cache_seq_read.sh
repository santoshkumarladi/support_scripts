#
# Copyright (c) 2014 Nutanix Inc. All rights reserved.
#
# Author: gdowding@nutanix.com
#
# $1 = number of disks
# $2 = num outstanding
# $3 = runtime
# $4 = block size
# $5 = extent_cache_kb
#
# This should be run with runtime>=300 and num_outstanding={1,2,4,8}

num_disks=$1
num_outstanding=$2
runtime=$3
block_size=$4
extent_cache_kb=$5

# Disk names and the ioengine depend on the hypervisor hosting the uvms.
io_engine="libaio"
for file_prefix in vd xvd sd; do
  test -b "/dev/${file_prefix}b" && break
done

UNAME=`uname`
if [[ $UNAME == Linux* ]]; then
  processes=`python -c "
processes=[]
for ii in range($1):
  processes.append(\"--name=process%s\" % (ii + 1))
  processes.append(\"--filename=/dev/$file_prefix%s\"%chr(ord(\"b\")+ii))
print \" \".join(processes)"`
elif [[ $UNAME == CYGWIN* ]]; then
  echo "cached read is not supported on $UNAME"
  exit -1
else
  echo "Unknown UVM OS"
  exit -1
fi

# Direct io needs to be alligned to 4k boundries.
size=`expr \( \( $extent_cache_kb / $num_disks \) / 4 \) \* 4`
ramp_time=`expr $runtime / 3`

sudo /usr/bin/fio --direct=1 --numjobs=1 --bs=$block_size --rw=read \
  --group_reporting --ioengine=$io_engine --ramp_time=$ramp_time\
  --runtime=$runtime --time_based --size=${size}kb --iodepth=$num_outstanding\
  $processes

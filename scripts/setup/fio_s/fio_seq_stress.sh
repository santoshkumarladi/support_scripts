#
# Copyright (c) 2016 Nutanix Inc. All rights reserved.
#
# Author: nick.neely@nutanix.com
#
# Args:
#     $1 (int): Number of disks
#     $2 (int): Size of disks
#     $3 (int): The total number of outstanding IOs
#     $4 (int): Block size
#     $5 (int): Runtime in seconds
#     $6 (int): Percentage writes (the rest will be reads)
#     $7 (int): The total number of IO threads
#

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
print \" \".join(disk_list)"`
elif [[ $UNAME == CYGWIN* ]]; then
  io_engine="windowsaio"
  disk_list='\\.\PhysicalDrive1'
  for i in `seq $1`; do if [ $i -ne 1 ]
  then disk_list=$disk_list' \\.\PhysicalDrive'$i; fi; done
else
  echo "Unknown UVM OS"
  exit -1
fi

. ./run_fio.sh

bail() {
  echo "Error: $@"
  exit 1
}

# Divide the total number of outstanding IOs between the workers.
inflight=$(( $3 / $7 ))
(( $inflight > 0 )) || bail "The per-worker queue depth must be at least one."

# Divide the total number of worker threads between the disks.
num_jobs=$(( $7 / $1 ))
(( $num_jobs > 0 )) || bail "Each disk must have at least one worker thread."

job_args=""
for d in $disk_list; do
  job_args="$job_args --name=$(basename $d) --filename=$d"
done

run_timed_fio $5 "fio.log" \
  --ioengine=$io_engine --numjobs=$num_jobs --group_reporting \
  --direct=1 --size=$2 --iodepth=$inflight --bs=$4 \
  --time_based --rw=rw --rwmixwrite=$6 \
  --randrepeat=0 --norandommap \
  --offset_increment=$(( 4 * 1024 * 1024 )) \
  $job_args
status=$?

echo
# This must be the last line.
echo "Test status: $status"
exit $status

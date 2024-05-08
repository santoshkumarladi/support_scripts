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

. ./run_fio.sh

# Perform verification every n blocks. A larger value increases the
# window during which an integrity issue can be detected, increases
# fio's memory overhead (fio stores verification metadata in memory),
# and increases the delay between when an error occurs and the issue is
# detected. The following value was determined empirically as a
# compromise between those factors.
VERIFY_BACKLOG=1000000

run_timed_fio $5 "fio.log" \
  --filename=$disk_list --name=file1 --ioengine=$io_engine --group_reporting \
  --direct=1 --size=$(( $1 * $2 )) --iodepth=$3 --bs=$4 \
  --time_based --rw=rw --rwmixwrite=$6 \
  --randrepeat=0 --norandommap \
  --do_verify=1 --verify=sha1 --verify_fatal=1 --verify_dump=1 \
  --verify_backlog=$VERIFY_BACKLOG
status=$?

echo
# This must be the last line.
echo "Test status: $status"
exit $status

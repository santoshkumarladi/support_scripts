for file_prefix in vd xvd sd; do
  test -b "/dev/${file_prefix}b" && break
done

UNAME=`uname`
if [[ $UNAME == Linux* ]]; then
  disk_list=`python -c "
disk_list=[]
for ii in range(12):
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
echo $disk_list
IFS=':' read -ra ADDR <<< "$disk_list"
for i in "${ADDR[@]}"; do
    echo "sudo /usr/bin/dd if=/dev/urandom of=$i bs=1M count=10000 conv=noerror,sync &"
    cmd="sudo /usr/bin/dd if=/dev/urandom of=$i bs=1M count=10000 conv=noerror,sync "
    nohup $cmd &
done

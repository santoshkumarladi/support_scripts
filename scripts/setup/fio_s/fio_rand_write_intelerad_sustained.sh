#
# Copyright (c) 2017 Nutanix Inc. All rights reserved.
#
# Author: amrut.shivaku@nutanix.com
#
# $1 = number of disks

# Disk names and the ioengine depend on the hypervisor hosting the uvms.
echo -e "size=4g" >> /home/nutanix/fio_s/fio_prof_intelerad
echo -e "name=sustained" >> /home/nutanix/fio_s/fio_prof_intelerad
for ((ii=1;ii<=$1;ii++))
do
  echo -e "[job$ii]" >> /home/nutanix/fio_s/fio_prof_intelerad;
  echo -e "directory=/opt/fiotest$ii" >> /home/nutanix/fio_s/fio_prof_intelerad;
done;

sudo /usr/bin/fio /home/nutanix/fio_s/fio_prof_intelerad

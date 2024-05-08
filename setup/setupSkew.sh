#! /bin/bash

set -x
echo " Setting cluster"

ncli license license-enforcement enable=false
sp_id=`ncli sp ls |grep 'Id '|awk {'print $3'}|rev|cut -f 1 -d :|rev`
ncli ctr create name=long_test_cont_1 sp-id=$sp_id enable-compression=true compression-delay=0 fingerprint-on-write=on on-disk-dedup=post_process 
ncli ctr create name=long_test_cont_2 sp-id=$sp_id enable-compression=true compression-delay=60 fingerprint-on-write=on on-disk-dedup=post_process 
ncli ctr create name=long_test_cont_3 sp-id=$sp_id enable-compression=true compression-delay=6 fingerprint-on-write=on on-disk-dedup=post_process 
ncli ctr create name=long_test_cont_4 sp-id=$sp_id enable-compression=true compression-delay=0 
  
ncli cluster add-to-name-servers servers=10.40.64.15,10.40.64.16
sleep 5

ncli cluster add-to-ntp-servers servers=sv2-ntp1.corp.nutanix.com,us.pool.ntp.org,ntp.dyn.nutanix.com

ncli user reset-password user-name=admin password=Nutanix.123
acli net.create vlan0 vlan=0
echo "sudo mkdir /mnt/long_test_cont_1;sudo mount localhost:/long_test_cont_1 /mnt/long_test_cont_1"
`sudo mkdir /mnt/long_test_cont_1;sudo mount localhost:/long_test_cont_1 /mnt/long_test_cont_1`
echo " wget http://endor.dyn.nutanix.com/agave/goldimages/kvm/CentOS7.2.tar.gz /mnt/long_test_cont_1 ; tar -xvzf /mnt/long_test_cont_1/CentOS7.2.tar.gz "
`wget http://endor.dyn.nutanix.com/agave/goldimages/kvm/CentOS7.2.tar.gz /mnt/long_test_cont_1 ; tar -xvzf /mnt/long_test_cont_1/CentOS7.2.tar.gz`
 /usr/local/nutanix/bin/acli image.create tiltS container=long_test_cont_1 image_type=kDiskImage source_url=http://10.41.70.50/images/tilting.qcow2

for ip in `svmips`; do echo $ip; ssh -q $ip "sudo yum install -y nfs-utils --nogpgcheck";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mkdir /mnt/archive";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount 10.40.231.197:/volume1 /mnt/archive";done;


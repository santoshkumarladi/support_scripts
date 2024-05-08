#! /bin/bash

set -x
echo " Setting cluster"

ncli license license-enforcement enable=false
sp_id=`ncli sp ls |grep 'Id '|awk {'print $3'}|rev|cut -f 1 -d :|rev`
#ncli ctr create name=aeslogan sp-id=$sp_id enable-compression=true compression-delay=60 fingerprint-on-write=on on-disk-dedup=post_process 
ncli ctr create name=aeslogan sp-id=$sp_id enable-compression=true compression-delay=60 fingerprint-on-write=on on-disk-dedup=post_process 
ncli ctr create name=aesl sp-id=$sp_id enable-compression=true compression-delay=0 fingerprint-on-write=on on-disk-dedup=post_process 
ncli ctr create name=aesg sp-id=$sp_id enable-compression=true compression-delay=60 fingerprint-on-write=on on-disk-dedup=post_process 
ncli ctr create name=aeslogan_c sp-id=$sp_id enable-compression=true compression-delay=0 
ncli ctr create name=aeslogan_d sp-id=$sp_id fingerprint-on-write=on on-disk-dedup=post_process
ncli ctr create name=aeslogan_c_d sp-id=$sp_id enable-compression=true compression-delay=0 fingerprint-on-write=on on-disk-dedup=post_process
  
ncli cluster add-to-name-servers servers=10.40.64.15,10.40.64.16
sleep 5
ncli cluster edit-params new-name=logan
ncli cluster edit-info external-ip-address=10.40.161.223
#ncli cluster edit-info external-data-services-ip-address=10.5.209.169
#ncli remote-site add name=falcon address-list=10.5.68.70 enable-compression=true

ncli cluster add-to-ntp-servers servers=sv2-ntp1.corp.nutanix.com,us.pool.ntp.org,ntp.dyn.nutanix.com

ncli user reset-password user-name=admin password=Nutanix.123
acli net.create vlan0 vlan=0
#sudo yum install -y nfs-utils

#for c in {1..120}
#do
#ncli pd create name=nsf1pd$c
#sleep 1
#ncli pd protect name=nsf1pd$c vm-names=centos_y1_pd_$c
#done 

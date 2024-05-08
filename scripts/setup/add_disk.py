#!/usr/bin/python

import sys,os
import string
import time
import json

def add_disk(patr,dtype):
    cmd = "source /etc/profile; /usr/local/nutanix/cluster/bin/disk_operator reset_partition_table "+patr 
    print cmd
    os.system(cmd)
    json = " /home/nutanix/.nested_ahv_disk_types.json"
    if dtype == 'SSD':
        dis = {patr:"SSD-SATA"}
    elif dtype == 'HDD'
        dis = {patr:"DAS-SATA"}
        
    with open('data.json', 'r+') as f:
        data = json.load(f)
        data.update({patr:"SSD-SATA"})
        f.seek(0)
        json.dump(data, f)
        f.truncate() 
        print json.dumps(data)
    cmd = "source /etc/profile; /usr/local/nutanix/cluster/bin/disk_operator  create_partition  "+patr 
    print cmd
    os.system(cmd)
    cmd = "source /etc/profile; /usr/local/nutanix/cluster/bin/disk_operator  get_disk_partitions "+patr 
    print cmd
    os.system(cmd)
    cmd = "sudo reboot"
    print cmd
    os.system(cmd)

def main():
        
    add_disk(sys.argv[1],sys.argv[2])

if __name__ == "__main__":
    main()

#!/usr/bin/python

import sys, getopt,os,re
import pandas as pd
import random
import string
import time
import itertools
import pexpect
import lxml
from collections import defaultdict


def isDiskFailing(cvm):
    ssh = "ssh "+cvm+" -l nutanix"
    ncli = " /home/nutanix/prism/cli/ncli "
    run = ssh +ncli+"disk get-remove-status "
    op = os.popen(run).read()
    op = op.strip()
    print "Disk fail --> "+op
    if op == '[None]':
        return 0
    else :
        return 1

def disk_fail(cvm,userid,wait):
    ssh = "ssh "+cvm+" -l "+userid
    did = '00059629-899d-17d2-4816-00e0ed932ec1::48' 
    typed = 'SSD'
    dsid = 'S456NY0KA00365'
    print did , typed , dsid
    if typed :
    #if typed != 'SSD-PCIe':
        cmd = ssh+" \"source /etc/profile; /usr/local/nutanix/cluster/bin/disk_operator disk_serial_to_block_device "+dsid+" \""
        print cmd
        op = os.popen(cmd).read()
        match = re.match(r'(.*)Block\s+Device:(.*)', op)
        if match is not None:
            dev  = match.groups()[1]
            print "The device is --> "+dev
            cmd = ssh+" \"source /etc/profile;  /home/nutanix/prism/cli/ncli disk rm-start force=false id="+did.split(':')[2]+" \""
            print cmd
            op = os.popen(cmd).read()
            print "op "+op
            mat = re.match(r'(.*)\s+Disk\s+removal\s+successfully\s+initiated(.*)', op)
            print mat
            #Disk removal successfully initiated
            if mat is None:
                print "Wait for the disk remove to complete "
                while isDiskFailing(cvm):
                    print "Another disk fail is in progress"
                    time.sleep(wait)
                #Successfully repartitioned disk /dev/sdf and added it to zeus
                if not isDiskFailing(cvm):
                    print "Repartion and Add the disk back "
                    cmd = ssh+" \"source /etc/profile; /usr/local/nutanix/cluster/bin/disk_operator --hades_rpc_timeout_secs=60 repartition_add_zeus_disk "+dev +"\""
                    print cmd
                    p = re.compile('Successfully\s+repartitioned\s+disk\s+'+dev+'\s+and\s+added\s+it\s+to\s+zeus')
                    ma = p.match( (os.popen(cmd).read()))
                    if ma is not None:
                        print "Successfully repartitioned disk"
        else :
            offset = offset+1

def main(argv):
    userid = 'nutanix'
    node='10.2.195.166'
    
    disk_fail(node,userid,120)

if __name__ == "__main__":
    main(sys.argv[1:])

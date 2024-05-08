#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import subprocess

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    lun = ''
    try:
        opts, args = getopt.getopt(argv,"hi:b:d:c:m:n:s:",["i=","b=","d=","con=","mntp=","ndrive=","dsize="])
    except getopt.GetoptError:
        print 'runTest.py -i <cvm> -b <breadth> -d <depth> -c <con> -m <mntp> -n <nodrive> -s <dsize>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'runTest.py -i <cvm> -b <breadth> -d<depth> -c<con> -m <mntp> -n <nodrive> -s <disk size>'
            sys.exit()
        elif opt in ("-i", "--cvm"):
            b = int(arg)
        elif opt in ("-b", "--breadth"):
            b = int(arg)
        elif opt in ("-d", "--depth"):
            d = int(arg)
        elif opt in ("-c", "--con"):
            con = arg
        elif opt in ("-n", "--ndrive"):
            ndrive = arg
        elif opt in ("-s", "--dsize"):
            dsize = arg
        elif opt in ("-m", "--mntp"):
            mntp = arg

    ssh = "ssh "+cvm+" -l "+userid+" /usr/local/nutanix/bin/acli -y"
    vmAddDisk(ssh,vname,container,dcount,dsize,lun,mntp,userid,passwd,b,d):

def vmAddDisk(ssh,vname,container,dcount,dsize,lun,mntp,userid,passwd,b,d):
    for i in range(dcount):
        cmd = ssh+" vm.disk_create "+uuid+" container="+container+ "create_size="+dsize
        print cmd
        os.system(cmd)
    cmd = "/usr/bin/lsblk -S -f -s "
    output = (os.popen(cmd).read()).split('\n')
    for i in range(1,len(output)-1):
        if outputi[i] not in ext4:
            line = output[i].split() 
            print line[0]
            runTheScript(line[0],mntp,userid,passwd,b,d)
            

def runTheScript(lun,mntp,userid,passwd,b,d):
    #sudo ./crtFD.py -i /mnt/dataBlock/testDI -b 5 -d 5
    run = " sudo umount -f "+mntp
    os.system(run)
    try :
        run = "sudo /usr/sbin/mkfs.ext4 -F -t ext4 "+lun
        print run
        subprocess.call(run,shell=True)
        run = "sudo mkdir -p "+mntp
        print run
        subprocess.call(run,shell=True)
        run = "sudo mount "+lun+" "+mntp
        print run
        subprocess.call(run,shell=True)
    except Exception as e:
        print ('wrongcommand does not exist')
        print e
        exit()

    run = " sudo /home/nutanix/scripts/setup/crtMFD.py -i " +mntp+ " -b "+str(b)+" -d "+str(d)+" &"
    print run
    os.system(run)
    time.sleep(60)
    run = " sudo /home/nutanix/scripts/setup/fileOpt.py -i " +mntp+ " -b "+str(b)+" -d "+str(d)+" &"
    print run
    os.system(run)



if __name__ == "__main__":
    main(sys.argv[1:])


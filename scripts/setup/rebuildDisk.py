#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import subprocess

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    b=d=2
    mntp="/mnt/dataMnt"
    s=2
    ops=0
    try:
        opts, args = getopt.getopt(argv,"hb:d:m:",["breadth=","depth=","mntp="])
    except getopt.GetoptError:
        print 'runTest.py -b <breadth> -d <depth> -m <mntp> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'runTest.py -b <breadth> -d <depth> -m <mntp> '
            sys.exit()
        elif opt in ("-b", "--breadth"):
            b = int(arg)
        elif opt in ("-d", "--depth"):
            d = int(arg)
        elif opt in ("-m", "--mntp"):
            mntp = arg

    cmd = " sudo kill $(ps aux | grep 'dataMnt' | grep -v rebuildDisk.py | awk '{print $2}') "
    print cmd
    os.system(cmd)
    cmd = "sudo umount -f $(mount | grep 'dataMnt' | awk '{print $1}') "
    print cmd
    os.system(cmd)
    vmAddDisk(mntp,userid,passwd,b,d)


def vmAddDisk(mntp,userid,passwd,b,d):
    #run = " sudo python /home/nutanix/scripts/fioWokload/FioWorkload.py &"
    #print run
    #os.system(run)
    cmd = "/usr/bin/lsblk -S -f -s | grep -v rom"
    output = (os.popen(cmd).read()).split('\n')
    for i in range(2,len(output)-1):
        line = output[i].split() 
        print "scsci device -> "+line[0]
        if line[0]:
            mnt = mntp+"/"+line[0]
            run = " sudo umount -f "+mnt
            os.system(run)
            try :
                run = "sudo /usr/sbin/mkfs.ext4 -F -t ext4 /dev/"+line[0]
                print run
                subprocess.call(run,shell=True)
            except Exception as e:
                print ('wrongcommand does not exist')
                print e
                exit()
            time.sleep(20)

            mnt = mntp+"/"+line[0]
            run = "sudo mkdir -p "+mnt
            print run
            subprocess.call(run,shell=True)
            try :
                run = "sudo mount /dev/"+line[0]+" "+mnt
                print run
                subprocess.call(run,shell=True)
            except Exception as e:
                print ('mount failed')
                print e
                exit()

if __name__ == "__main__":
    main(sys.argv[1:])


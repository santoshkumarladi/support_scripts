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
    alls=0
    ops=0
    try:
        opts, args = getopt.getopt(argv,"hb:d:m:s:a:",["breadth=","depth=","mntp=","opt=","all="])
    except getopt.GetoptError:
        print 'runTest.py -b <breadth> -d <depth> -m <mntp> -s <opt>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'runTest.py -b <breadth> -d <depth> -m <mntp> -s<opt>'
            sys.exit()
        elif opt in ("-b", "--breadth"):
            b = int(arg)
        elif opt in ("-d", "--depth"):
            d = int(arg)
        elif opt in ("-m", "--mntp"):
            mntp = arg
        elif opt in ("-s", "--opt"):
            ops = int(arg)
        elif opt in ("-a", "--all"):
            alls = int(arg)

    print " opt -> "+str(ops)+ " alls "+str(alls)
    vmAddDisk(mntp,userid,passwd,b,d,ops,alls)


def vmAddDisk(mntp,userid,passwd,b,d,opt,alls):
    #run = " sudo python /home/nutanix/scripts/fioWokload/FioWorkload.py &"
    #print run
    #os.system(run)
    cmd = "/usr/bin/lsblk -S -f -s | grep -v rom"
    output = (os.popen(cmd).read()).split('\n')
    for i in range(2,len(output)-1):
        if 'ext4' in output[i] :
            alls = 1
            line = output[i].split() 
            print "scsci device -> "+line[0]
            if line[0]:
                mnt = mntp+"/"+line[0]
                runTheScript(line[0],mntp,userid,passwd,b,d,opt,alls)
        else :
            alls = 1
            line = output[i].split() 
            print "create FS ext4 -> "+line[0]
            if line[0]:
                mnt = mntp+"/"+line[0]
                runTheScript(line[0],mntp,userid,passwd,b,d,opt,alls)

def runTheScript(lun,mnt,userid,passwd,b,d,opt,alls):
    mntp = mnt+"/"+lun
    if alls:
        #sudo ./crtFD.py -i /mnt/dataBlock/testDI -b 5 -d 5
        #cmd = "sudo kill $(ps aux | grep 'dataMnt'|grep -v grep | awk '{print $2}')"
        #print cmd
        #os.system(cmd)
        run = " sudo umount -f "+mntp
        os.system(run)
        try :
            run = "sudo /usr/sbin/mkfs.ext4 -F -t ext4 /dev/"+lun
            print run
            subprocess.call(run,shell=True)
        except Exception as e:
            print ('wrongcommand does not exist')
            print e
            exit()
        time.sleep(20)
    
    run = "sudo mkdir -p "+mntp
    print run
    subprocess.call(run,shell=True)
    try :
        run = "sudo mount /dev/"+lun+" "+mntp
        print run
        subprocess.call(run,shell=True)
    except Exception as e:
        print ('mount failed')
        print e
        exit()
    
    if opt == 1:
        #sudo /home/nutanix/scripts/setup/fops.py -i /mnt/dataMnt/sdb -n 20 -r 50 -s 500g
        run = " sudo /home/nutanix/scripts/setup/fops.py -i " +mntp+ " -n 20 -r 50 -s 500gb </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)
        time.sleep(6)
        # ./fileStripTN pathname=<file path > fs=<file size> bs=<block size> nf=<no of files>
        run = " sudo /home/nutanix/scripts/automation/fileStripTN pathname="+mntp+" fs=1G bs=1M nf=100 </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)
        run = " sudo /home/nutanix/scripts/automation/fop -H 0 -W 0 -o cdcdcdcd -s 10k -t 15 -n 100000 "+mntp+" </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)

    if opt == 2:
        run = " sudo /home/nutanix/scripts/setup/crtMFD.py -i " +mntp+ " -b "+str(b)+" -d "+str(d)+" </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)
        time.sleep(6)
        #./comprFileFullop pathname=<file path > fs=<file size> nf <no of files> rc=<no iterations>
        run = " sudo /home/nutanix/scripts/automation/comprFileT pathname=" +mntp+ " fs=1M nf=1000 rc=10000 </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)
        run = "sudo /home/nutanix/scripts/automation/fop -H 0 -W 0 -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd -s 100k -t 15 -n 100000 "+mntp+" </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)

    if opt == 3:
        run = " sudo /home/nutanix/scripts/setup/fileOpt.py -i " +mntp+ " -b "+str(b)+" -d "+str(d)+" </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)
        #Usage: ./zombFileMulN1 pathname=<file path > fs=<file size> bs=<block size>
        run = "sudo /home/nutanix/scripts/automation/zombFileMulN1 pathname="+mntp+" fs=100K bs=10K </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)
        run = "sudo /home/nutanix/scripts/automation/fop -H 0 -W 0 -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd -s 100g -t 15 -n 1 "+mntp+" </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)

    if opt == 4:
        run = " sudo /home/nutanix/scripts/automation/fop -H 2 -W 10,100,500,1000  -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd  -f 10k,20,20,10 -n 300 -s 10k,20,10k,100k -t 10 -O RD "+mntp+" </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)

    
if __name__ == "__main__":
    main(sys.argv[1:])


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

    cmd = " sudo kill $(ps aux | grep 'dataMnt' | grep -v stressRunBig.py | awk '{print $2}') "
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
        if 'ext4' in output[i] :
            line = output[i].split() 
            print "scsci device -> "+line[0]
            if line[0]:
                opt = 1 
                mnt = mntp+"/"+line[0]
                runTheScript(line[0],mntp,userid,passwd,b,d,opt)
        else :
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

def runTheScript(lun,mnt,userid,passwd,b,d,opt):
    mntp = mnt+"/"+lun
    
    run = "sudo rm -rf "+mntp+" ; sudo mkdir -p "+mntp
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

        run = " sudo /home/nutanix/scripts/automation/fop -H 2 -W 10,100,500,1000  -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd  -f 10k,20,20,10 -n 300 -s 10k,20,10k,100k -t 10 -O RD "+mntp+" </dev/null>/dev/null 2>&1 &"
        print run
        os.system(run)

    
if __name__ == "__main__":
    main(sys.argv[1:])


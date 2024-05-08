#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect

def sshCopyid(ip):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    try :
        cmd = "ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o \"StrictHostKeyChecking no\" nutanix@"+str(ip)
        print cmd
        child = pexpect.spawn(cmd)
        r=child.expect ('assword:')
        print "Outp"+str(r)
        if r==0:
            child.sendline (passwd)
        child.interact()
        child.close()
    except Exception as e:
        print "Oops Something went wrong buddy"
        #print e


def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    wait = 3600
    try:
        opts, args = getopt.getopt(argv,"hc:w:",["cvm=","wait="])
    except getopt.GetoptError:
        print 'runScavenge.py -c <cvm> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'runScavenge.py -c <cvm> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid
    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    print output[0]
    svmips = output[0].split()
    while 1:
        for svmip in svmips:
            sshCopyid(svmip)
            run = "sudo mkdir /mnt/cdp_fit; sudo mount 10.40.167.227:/cdp_fit /mnt/cdp_fit"
            print run
            os.system(run)
            run = "ssh "+svmip+" -l nutanix \"sudo nohup /usr/local/nutanix/bin/scavenger.py --paths=/home/nutanix/data/logs,/home/nutanix/data/cores,/home/nutanix/data/binary_logs --timeout_secs=3600 --threshold_size_MB 100,200,100 --interval_secs 900 --archive_url=local:////mnt/cdp_fit --compression_level=0\" &"
            print run
            os.system(run)
        time.sleep(wait)

if __name__ == "__main__":
    main(sys.argv[1:])


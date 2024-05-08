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
    patr = ''
    try:
        opts, args = getopt.getopt(argv,"hc:p:",["cvm=","pat="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm>  -p <pattern>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm>  -p <pattern>'
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--pat"):
            patr = arg

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid

    while 1:
        runS(ssh,cvm,patr)
        time.sleep(1200)

def runS(ssh,cvm,patr):
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "
    userid = 'nutanix'
    ip = ''
    run = ssh+acli +" vm.list | grep  \""+patr+"\" | grep -v \"VM name\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(len(output)-1):
        if output[i]:
            (vm,uuid) = output[i].split()
            run = ssh +acli+" vm.power_cycle "+vm
            print run
            os.system(run)

if __name__ == "__main__":
    main(sys.argv[1:])


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
    wait=1
    try:
        opts, args = getopt.getopt(argv,"hc:p:w:",["cvm=","pat=","wait="])
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
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid
    while 1:
        vmOpp(ssh,cvm,patr)
        time.sleep(wait) 

def vmOpp(ssh,cvm,patr):
    acli = " /usr/local/nutanix/bin/acli -y"
    userid = 'nutanix'
    state = ["on","off"]
    for st in state:
        if patr == "" :
            run = ssh+acli +" vm.list power_state="+st+" | grep -v \"VM name\""
            if st == 'on':
                onlist = (os.popen(run).read()).split('\n')
            else :
                offlist = (os.popen(run).read()).split('\n')
        else:
            run = ssh+acli +" vm.list power_state="+st+" | grep  \""+patr+"\" | grep -v \"VM name\""
            if st == 'on':
                onlist = (os.popen(run).read()).split('\n')
            else :
                offlist = (os.popen(run).read()).split('\n')
    print run
    for i in range(len(onlist)-1):
        if onlist[i]:
            (vm,uuid) = onlist[i].split()
            run = ssh +acli+" vm.off "+vm
            print run
            os.system(run)
    for i in range(len(offlist)-1):
        if offlist[i]:
            (vm,uuid) = offlist[i].split()
            run = ssh +acli+" vm.on "+vm
            print run
            os.system(run)

if __name__ == "__main__":
    main(sys.argv[1:])


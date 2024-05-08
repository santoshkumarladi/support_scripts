#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import threading
from collections import defaultdict 


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

def getHostVmList(cvm,host):
    hostvm = [] 
    ssh = "ssh "+cvm+" -l nutanix "
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    cmd = ssh+acli+" host.list_vms "+host
    print cmd
    op = (os.popen(cmd).read()).split('\n')
    for i in range(1,len(op)-1):
        hostvm.append(op[i].split()[0])
    return hostvm

def checkCvm(cvm,hostip,opt):
    ssh = "ssh "+cvm+" -l nutanix "
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "
    hostvms = getHostVmList(cvm,hostip)

    for vm in hostvms:
        run = ssh+acli+" vm."+opt+" " +vm
        print run
        os.system(run)
       
def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    wait = 1200
    opr = 'on'

    try:
        opts, args = getopt.getopt(argv,"hc:i:o:w:",["cvm=","host=","opt=","wait="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -o <opr> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -o <opr> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-i", "--host"):
            hosts = arg
        elif opt in ("-o", "--opt"):
            opr = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)
    svmips = hosts.split(",")
    for  hvmip in svmips:
        checkCvm(cvm,hvmip,opr)



if __name__ == "__main__":
    main(sys.argv[1:])


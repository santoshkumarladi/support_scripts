#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import threading
import pexpect


userid = 'nutanix'
passwd = 'nutanix/4u'
def delVmbyPattern(ssh,vname):
    run = ssh +" vm.list"+" | grep \""+vname+"\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(1,len(output)-1):
        #VM name  VM UUID
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.delete "+uuid
        print cmd
        os.system(cmd)
            
def killS(wait):
    time.sleep(wait)
    cmd = "kill $(ps aux | grep 'compTest.py' | awk '{print $2}')"
    os.system(cmd)

def main(argv):
    cmd = ''
    cvm = ''
    try:
        opts, args = getopt.getopt(argv,"hi:",["cvm="])
    except getopt.GetoptError:
        print 'runStreeMul.py -i <cvm> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'runStreeMul.py -i <cvm> '
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvm = arg 
    sshCopyid(cvm)
    runS(cvm)

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

def runS(cvm):
    vmlist = []
    wait = 10

    #ssh 10.46.32.65 -l nutanix ls
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    run = ssh +acli+" vm.list | grep -v \"time\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(2,len(output)-1):
        #VM name  VM UUID                               
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        (vm,uuid) = output[i].split()
        run = ssh +ncli+" vm list name="+vm+" | grep \"VM IP Addresses\""
        print run
        match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
        if match is not None:
            ip = match.group()
            print vm+" "+uuid+" "+ip
            vmlist.append({'uuid':uuid,'vm':vm,'ip':ip})
            sshCopyid(ip)
            cmd = "ssh "+ip+" -l nutanix \" df -kh . \" "
            print cmd
            os.system(cmd)
            cmd = "ssh "+ip+" -l nutanix \"  ps -eaf | grep dataMnt \" "
            print cmd
            os.system(cmd)
            """
            #run = ssh +acli+" vm.power_cycle "+vm
            #print run
            #os.system(run)
            #time.sleep(20)
            cmd = "ssh "+ip+" -l nutanix \" sudo kill \$(ps aux | grep 'dataMnt' | awk '{print \$2}')  \""
            print cmd
            os.system(cmd)
            cmd = "ssh "+ip+" -l nutanix \"sudo umount -f \$(mount | grep 'dataMnt' | awk '{print \$1}')   \""
            print cmd
            os.system(cmd)
            #cmd = "ssh "+ip+" -l nutanix \" rm -rf /home/nutanix/scripts ; rm -rf /home/nutanix/data/cores/* \""
            cmd = "ssh "+ip+" -l nutanix \" sudo rm -rf /home/nutanix/data/cores/* \""
            print cmd
            os.system(cmd)
            cmd = "ssh "+ip+" -l nutanix \" sudo rm -rf /mnt/dataMnt/ \" &"
            print cmd
            os.system(cmd)
            """
if __name__ == "__main__":
    main(sys.argv[1:])


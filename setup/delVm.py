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
            

def main(argv):
    pat = ''
    cvm = ''
    try:
        opts, args = getopt.getopt(argv,"hi:p:",["cvm=","pat="])
    except getopt.GetoptError:
        print 'runStreeMul.py -i <cvm> -p <pat>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'runStreeMul.py -i <cvm> -p <pat>'
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvm = arg 
        elif opt in ("-p", "--pat"):
            pat = arg 
    runS(cvm,pat)

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

def delSn(ssh,output,start,offset):
    length = start+offset
    for i in range(start,length-1):
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.delete "+uuid
        print cmd
        os.system(cmd)


def runS(cvm,vname):
    threads = []
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    for  svmip in svmips:
        sshCopyid(svmip)
    run = ssh +acli+" vm.list"+" | grep \""+vname+"\""
    print run
    output = (os.popen(run).read()).split('\n')
    offset = len(output)/len(svmips)
    start =2 

    for svmip in svmips:
        ssh = "ssh "+svmip+" -l "+userid
        t = threading.Thread(target=delSn, args=(ssh+acli,output,start,offset,))
        start = start+offset
        threads.append(t) 

    for x in threads:
        x.start()

    for x in threads:
        x.join()

if __name__ == "__main__":
    main(sys.argv[1:])


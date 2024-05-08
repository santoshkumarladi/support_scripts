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

def getHostVmList(cvm):
    hostvm = defaultdict(list)
    ssh = "ssh "+cvm+" -l nutanix "
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    run = "ssh "+cvm+" -l nutanix /usr/local/nutanix/cluster/bin/hostips"
    output = (os.popen(run).read()).split('\n')
    hostips = output[0].split()
    print hostips
    
    for host in hostips:
        try :
            cmd = ssh+" ssh root@"+host+" virsh list | grep CVM"
            print cmd
            cvm = (os.popen(cmd).read()).split()[1]
            if 'CVM' in cvm :
                cmd = ssh+acli+" host.list_vms "+host+" | grep -v vgclient | grep -v bigVm"
                print cmd
                op = (os.popen(cmd).read()).split('\n')
                hostvm[cvm] = []
                for i in range(1,len(op)-1):
                     hostvm[cvm].append(op[i].split()[0])
                     print op[i].split()[0] 
        except:
            print "Failed to get the CVM usage"
    return hostvm

def checkCvmCpuUse(svm,cvm,hostvms,cpu):
    ssh = "ssh "+svm+" -l nutanix "
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "
    cmd = ssh+ncli+" vm list-stats name="+cvm+" | grep \"CPU Usage Percent\""
    print cmd
    cpuP = (os.popen(cmd).read()).split(':')[1].strip()
    cpuP = int(float(cpuP.rstrip("%")))
    print "Current cpu usage is -> "+str(cpuP)+" required cpu usage is -> "+str(cpu)
    if cpuP > cpu:
        for vm in hostvms:
            run = ssh+acli+" vm.off "+vm
            print run 
            os.system(run)
            cmd = ssh+"links -dump http://127.0.0.1:2009/h/vars?regex=.%2atotal.%2aoplog_bytes"
            os.system(cmd)
    else :
        for vm in hostvms:
            cmd = ssh+"links -dump http://127.0.0.1:2009/h/vars?regex=.%2atotal.%2aoplog_bytes"
            os.system(cmd)
            run = ssh+acli+" vm.on "+vm
            print run
            os.system(run)
        if not hostvms:
            cmd = ssh+"links -dump http://127.0.0.1:2009/h/vars?regex=.%2atotal.%2aoplog_bytes"
            os.system(cmd)
            run = ssh+"\""+acli+" vm.on \*\""
            print run
            os.system(run)
            time.sleep(20)
            cmd = ssh+"links -dump http://127.0.0.1:2009/h/vars?regex=.%2atotal.%2aoplog_bytes"
            os.system(cmd)
       
def get_svmips(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    """
    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    if op :
        output = op.split('\n')
        for i in range(1,len(output)):
            if output[i].split()[4] != 'False':
                svmips.append(output[i].split()[-1])
    """
    return svmips

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    cpu = 70
    wait = 1200

    try:
        opts, args = getopt.getopt(argv,"hc:p:w:",["cvm=","cpu=","wait="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -p <cpu> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -p <cpu> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--cpu"):
            cpu = int(arg)
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    svmips = get_svmips(cvm)
    for  svmip in svmips:
        sshCopyid(svmip)
    runS(cvm,userid,passwd,cpu,wait)


def runS(cvm,userid,passwd,cpu,wait):
    
    print "Wait ---> "+str(wait)
    while 1:    
        threads = []
        hostvm = {}
        try :
            svmips = get_svmips(cvm)
            svm = svmips[random.randint(0,len(svmips)-1)]
            hostvm = getHostVmList(svm)
    
            for cvmn in hostvm.keys():    
                svm = svmips[random.randint(0,len(svmips)-1)]
                t = threading.Thread(target=checkCvmCpuUse, args=(svm,cvmn,hostvm[cvmn],cpu,))
                threads.append(t)

            for x in threads: 
                x.start()

            for x in threads: 
                x.join()

        except Exception as e:
            print "Oops Something went wrong buddy + wait and restart "
        time.sleep(wait)

if __name__ == "__main__":
    main(sys.argv[1:])


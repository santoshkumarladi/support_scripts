#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import threading
from collections import defaultdict 


def sshCopyid(ip):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    rsa_key = '\(yes\/no\)\?'
    prompt = "assword:"
    non_rsa='you wanted were added.'
    userid="nutanix"

    cmd = "ssh-keygen -R "+str(ip)
    os.system(cmd)
    cmd = " /usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no "+userid+"@"+str(ip)
    print cmd
    child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no %s@%s'%(userid,ip))
    #r=child.expect ('you wanted were added.')
    r= child.expect([non_rsa,rsa_key,prompt,pexpect.EOF],timeout=30)
    print "Outp"+str(r)
    if r==0:
        print "Outp 0"
        child.interact()
        child.close()
    elif r==1:
        print "Outp 1"
        child.sendline('yes')
        child.expect(prompt)
        child.sendline(passwd)
    elif r==2:
        print "Outp 2"
        child.sendline(passwd)
    elif r==3:
        print "Outp 3"
        child.sendline(passwd)
        child.interact()
        child.close()
    else :
        print "Outp 4"
        child.expect(prompt)
        child.sendline(passwd)

    child.interact()
    child.close()

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

def checkCvmCpuUse(svm,cvm,hostvms,power):
    ssh = "ssh -o ConnectTimeout=10 "+svm+" -l nutanix "
    acli = " /usr/local/nutanix/bin/acli -y"
    for vm in hostvms:
            run = ssh+acli+" vm."+power+" " +vm
            print run 
            os.system(run)
            cmd = ssh+"links -dump http://127.0.0.1:2009/h/vars?regex=.%2atotal.%2aoplog_bytes"
            os.system(cmd)
            cmd = ssh+'links --dump http:0:2009/vdisk_oplog_client_replica_stats'
            os.system(cmd)
       
def get_svmips(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh -o ConnectTimeout=10 "+cvm+" -l nutanix"
    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    if op :
        output = op.split('\n')
        for i in range(1,len(output)):
            print output[i].split()[4]
            if output[i].split()[4] != 'False':
                svmips.append(output[i].split()[-1])
                #print output[i].split()[-1]
        return svmips

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    cpu = 70
    wait = 1200

    try:
        opts, args = getopt.getopt(argv,"hc:p:w:",["cvm=","cpu=","wait="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -p <power> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -p <cpu> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--cpu"):
            cpu = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm)
    svmips = get_svmips(cvm)
    for  svmip in svmips:
        sshCopyid(svmip)

    runS(cvm,userid,passwd,cpu,wait)


def runS(cvm,userid,passwd,cpu,wait):
    power = ["on","off"] 
    i = 0
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh -o ConnectTimeout=10 "+cvm+" -l nutanix"
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
                t = threading.Thread(target=checkCvmCpuUse, args=(svm,cvmn,hostvm[cvmn],power[i],))

                threads.append(t)

            for x in threads: 
                x.start()

            for x in threads: 
                x.join()

            if i < 1 :
                i = i+1
            else :
                i = 0

        except Exception as e:
            run = ssh+" \""+acli+"vm.off \* \" &"
            print run 
            os.system(run)
            print "Oops Something went wrong buddy + wait and restart "
        time.sleep(wait)

if __name__ == "__main__":
    main(sys.argv[1:])


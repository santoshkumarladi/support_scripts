#!/usr/bin/python

import sys, getopt,os,re
import pandas as pd
import random
import string
import time
import datetime
import pexpect
import itertools
import subprocess

def wait_for_system(ip_add):
    print("Waiting for the system to come back up...")
    while subprocess.call(["ping", "-c", "1", "-W", "1", ip_add], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
        time.sleep(1)
    print("System is up and accessible.")

def sshCopyid(ip):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    cmd = "ssh-keygen -R "+str(ip)
    os.system(cmd)
    try :
        cmd = " /usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@"+str(ip)
        print cmd
        child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@%s'%(ip))
        r=child.expect ('you wanted were added.')
        print "Outp"+str(r)
        if r==1:
            cmd = " ssh "+str(ip)+" nutanix -l pwd"
            print cmd
            child = pexpect.spawn('ssh %s nutanix -l pwd'%(ip))
            rsa_key = '\(yes\/no\)\?'
            prompt = "Password:"
            i = child.expect([rsa_key,prompt,""])
            if i==0:
                child.sendline('yes')
                child.expect(prompt)
                child.sendline(passwd)
            elif i==1:
                child.sendline(passwd)
            else:
                child.sendline(passwd)
        child.interact()
        child.close()
    except Exception as e:
        print "Oops Something went wrong buddy"
        #print e


def check_failnode(cvm):
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"

    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    #print "Op ---> "+op
    if op :
        output = op.split('\n')
        for i in range(1,len(output)-1):
            if output[i].split()[4] == 'True':
                print output[i].split()[-1]
                return output[i].split()[-1]

    else :
        print "return the down cvm -- > "+cvm
        return cvm


def get_svmips(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    print "Op ---> "+op
    if op :
        output = op.split('\n')
        for i in range(1,len(output)):
            if output[i].split()[4] != 'False':
                print output[i].split()[7]
                svmips.append(output[i].split()[7])

        return svmips


def get_hostips(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    print "Op ---> "+op
    if op :
        output = op.split('\n')
        for i in range(1,len(output)):
            if output[i].split()[4] != 'False':
                svmips.append(output[i].split()[1])

        return svmips


def isDiskFailing(cvm):
    ssh = "ssh "+cvm+" -l nutanix"
    ncli = " /home/nutanix/prism/cli/ncli "
    run = ssh +ncli+"disk get-remove-status | grep \"Host Name\""
    op = os.popen(run).read()
    print "Disk fail --> "+op
    if op :
        op = os.popen(run).read().split(':')
        op = op[1].strip()
        return op
    else :
        return None

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    iuserid = 'ADMIN'
    ipasswd = 'ADMIN'
    wait = 60
    timeout = 1200
    chost = {}
    cvmreboot=1
    count= 10

    try:
        opts, args = getopt.getopt(argv,"hc:u:p:r:t:n:w:",["cvm=","userid","passwd","cvmre=","count=","timeout=","wait="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-u", "--userid"):
            iuserid = arg
        elif opt in ("-r", "--cvmre"):
            cvmreboot =  int(arg)
        elif opt in ("-p", "--passwd"):
            ipasswd = arg
        elif opt in ("-n", "--count"):
            count = int(arg)
        elif opt in ("-t", "--timeout"):
            timeout = int(arg)
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    run = ssh+" /usr/local/nutanix/cluster/bin/ipmiips"
    print run
    output = (os.popen(run).read()).split('\n')
    ipmips = output[0].split()
    print ipmips
 
    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    for  (svmip,ipmip) in itertools.izip(svmips,ipmips):
        sshCopyid(svmip)
        chost[ipmip] = svmip
 
    random.shuffle(ipmips)
    #interval = int(wait*8)

    while 1:
        cvm = check_failnode(cvm)
        ip = isDiskFailing(cvm)
        #ipmip = ipmips[random.randint(0,len(ipmips)-1)]
        print("----> "+str(timeout))
        if cvmreboot:
            creboot(svmips,userid,count,ip,wait)
            time.sleep(timeout)
        else :

            if ipmips:
                ipmip = ipmips.pop()
            else :
                run = ssh+" /usr/local/nutanix/cluster/bin/ipmiips"
                print run
                output = (os.popen(run).read()).split('\n')
                ipmips = output[0].split()
                ipmip = ipmips.pop()
            #random.shuffle(svmips)
            if ipmip != ip :
                runS(cvm,ipmip,svmips,chost,iuserid,ipasswd,wait)
                time.sleep(timeout)

def creboot(svmips,userid,count,ip,wait):
    random.shuffle(svmips)
    for svm in svmips:
        if ip != svm :
            for i in range(count):
                ssh = "ssh "+svm+" -l "+userid
                print "Before cvm reboot "+str(datetime.datetime.now())+" "+svm
                cmd = ssh+" sudo reboot -f"
                print cmd
                os.system(cmd) 
                wait_for_system(svm)
                time.sleep(wait)

def runS(cvm,ipmip,svmips,chost,userid,passwd,wait):
    for svmip in svmips:
        print "Before cvm reboot "+str(datetime.datetime.now())+" "+chost[ipmip]
        cmd = "/usr/bin/ipmitool  -H " +ipmip+" -U "+str(userid)+" -P "+str(passwd)+" chassis power off "
        print cmd
        os.system(cmd)
        time.sleep(wait)
        cmd = "/usr/bin/ipmitool  -H " +ipmip+" -U "+str(userid)+" -P "+str(passwd)+" chassis power on "
        print cmd
        os.system(cmd)
        time.sleep(wait)
        print " After reboot wait --> "+str(datetime.datetime.now())

if __name__ == "__main__":
    main(sys.argv[1:])


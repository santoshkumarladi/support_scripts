#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import threading
import itertools
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
    print run
    output = (os.popen(run).read()).split('\n')
    hostips = output[0].split()
    #print hostips

    for host in hostips:
        try :
            cmd = ssh+" ssh root@"+host+" virsh list | grep CVM"
            print cmd
            cvm = (os.popen(cmd).read()).split()[1]
            hostvm[host] = cvm
        except:
            print "Failed to get the CVM usage"
    return hostvm


def checkCvmCpuUse(svm,cvm):
    ssh = "ssh "+svm+" -l nutanix "
    ncli = " /home/nutanix/prism/cli/ncli "
    cmd = ssh+ncli+" vm list-stats name="+cvm+" | grep \"CPU Usage Percent\""
    print cmd
    cpu = (os.popen(cmd).read())
    print cpu
    if cpu:
        cpuP = cpu.split(':')[1].strip()
        cpuP = int(float(cpuP.rstrip("%")))
        print "Current cpu usage is -> "+str(cpuP)
       
def get_svmips(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    return svmips

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    cpu = 70
    wait = 1200

    try:
        opts, args = getopt.getopt(argv,"hc:w:",["cvm=","wait="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    svmips = get_svmips(cvm)
    for  svmip in svmips:
        sshCopyid(svmip)
    runS(svmips,cvm,userid,passwd,wait)


def runS(svmips,cvm,userid,passwd,wait):
    
    print "Wait ---> "+str(wait)
    while 1:    
        threads = []
        hostvm = {}

        try :
            hostvm = getHostVmList(cvm)
            hosts = hostvm.keys()
            print hosts , svmips
            for cvmn,svm in itertools.izip (hosts,svmips):    
                checkCvmCpuUse(svm,hostvm[cvmn])
            #for cvmn,svm in itertools.izip (hosts,svmips):    
            #    t = threading.Thread(target=checkCvmCpuUse, args=(svm,hostvm[cvmn],))
            #    threads.append(t)

            #for x in threads: 
            #    x.start()

            #for x in threads: 
            #    x.join()

        except Exception as e:
            print "Oops Something went wrong buddy + wait and restart "
        time.sleep(wait)

if __name__ == "__main__":
    main(sys.argv[1:])


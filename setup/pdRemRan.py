#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import threading

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


def pdRemSnap(run,cvm,start,off,out):
    print "start the restore range "+str(start) +" off "+str(off)
    i = 0
    while i < off:
        if out[start]:
            (tmp,pd) = out[start].split(":")
            cmd = run + " pd ls-snaps name="+pd.strip()+" | grep Id | grep -v \"VM Id\""
            print cmd
            snapshots = (os.popen(cmd).read()).split('\n')
            if snapshots :
                snap = snapshots[random.randint(1,len(snapshots)-1)]
                print "The snapshot --> "+snap
                (tmp,sid) = snap.split(":")
                cmd = run + " pd rm-snap name="+pd.strip()+" snap-ids="+sid.strip()
                print cmd
                os.system(cmd)
        start = start+1
        i=i+1


def get_svmips(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh +acli+"host.list "
    #print run

    op = os.popen(run).read()
    op = op.strip()
    #print "Op ---> "+op
    if op :
        output = op.split('\n')
        for i in range(1,len(output)):
            if output[i].split()[4] != 'False':
                #print output[i].split()[7]
                svmips.append(output[i].split()[7])

        return svmips

def pdDelSnap(run,cvm,start,off,out):
    print "start the delete on range "+str(start) +" off "+str(off)
    i = 0
    while i < off:
        if out[start]:
            (tmp,pd) = out[start].split(":")
            cmd = run +"pd clear-schedules name="+pd.strip()
            print cmd
            os.system(cmd)
            cmd = run + " pd rm-snap name="+pd.strip()+" clear-all=true "
            print cmd 
            os.system(cmd)
            #time.sleep(120)
            #pd list name=testPD_long_run_vm_test29
            cmd = run +" pd list name="+pd.strip()+" | grep \"VM Name\" "
            print cmd
            op = (os.popen(cmd).read())
            #if 'None' not in op :
            if op :
                try:
                    vm = op.split(":")[1]
                    cmd = run +" pd unprotect name="+pd.strip()+" vm-names="+vm.strip()
                    print cmd
                    os.system(cmd)
                    cmd = run + " pd remove name="+pd.strip()
                    print cmd
                    os.system(cmd)
                except Exception as e:
                    print op

        i = i+1
        start = start+1

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    pat = ''
    wait = 1200
    try:
        opts, args = getopt.getopt(argv,"hc:p:",["cvm=","pat=","wait="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--pat"):
            pat = arg
        elif opt in ("-w", "--wait"):
            pat = int(arg)

    sshCopyid(cvm)

    run = "ssh "+cvm+" -l "+userid +" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    for  svmip in svmips:
        sshCopyid(svmip)

    svmips = get_svmips(cvm)
    cvm = svmips.pop()
    while 1:
        runS(cvm,pat)
        time.sleep(wait)

def runS(cvm,pat):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    threads = []

    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    svmips = get_svmips(cvm)
    start =2
    if pat :
        cmd = ssh +ncli +"pd list | grep \"Protection Domain\" | grep \""+pat+"\""
    else :
        cmd = ssh +ncli +"pd list | grep \"Protection Domain\""
    print cmd
    out = (os.popen(cmd).read()).split('\n')
    off = len(out)/len(svmips)
    #pdRemSnap(ssh+ncli,cvm,start,off,out)
    for svmip in svmips:
        ssh = "ssh "+svmip+" -l "+userid
        print svmip,start,off
        t = threading.Thread(target=pdRemSnap, args=(ssh+ncli,svmip,start,off,out,))
        start = start+off
        threads.append(t)
        #time.sleep(120)

    for x in threads:
        x.start()

    for x in threads:
        x.join()
if __name__ == "__main__":
    main(sys.argv[1:])


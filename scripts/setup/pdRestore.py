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


def pdCreate(run,vm,nosnap,remote):
    cmd = run +" pd create name=testPD_"+vm
    print cmd
    os.system(cmd)
    cmd = run +" pd protect name=testPD_"+vm+" vm-names="+vm+" cg-name=testCG"+vm
    print cmd
    os.system(cmd)
    print "_______________________________________> "+remote
    nosnap=8
    if remote:
        cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" remote-retention="+remote+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
        print cmd
    else:
        cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
        print cmd

    os.system(cmd)
    nosnap=10
    cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" every-nth-hour=6 start-time=\\\"02/14/2018 18:30:00 UTC\\\"\""
    print cmd
    os.system(cmd)
    nosnap=5
    cmd = run +"\" pd add-daily-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" start-time=\\\"02/14/2018 09:30:00 UTC\\\"\""
    print cmd
    os.system(cmd)

def pdCre(run,vm):
    cmd = run +" pd create name=testPD_"+vm
    print cmd
    os.system(cmd) 
    cmd = run +" pd protect name=testPD_"+vm+" vm-names="+vm+" cg-name=testCG"+vm
    print cmd
    os.system(cmd) 
    cmd = run +" pd add-hourly-schedule name=testPD_"+vm+" local-retention=0 every-nth-hour=1"
    print cmd
    os.system(cmd)

def pdUpdate(ssh,ncli,acli,cvm,nosnap):
    run = ssh+ncli
    cmd = ssh +acli+" vm.list | grep -v \"VM name\" "
    print cmd
    vmoutput = (os.popen(cmd).read()).split('\n')

    for i in range(0,len(vmoutput)-1):
        (vm,uuid) = vmoutput[i].split()
        cmd = run +" pd unprotect name=testPD_"+vm+" vm-names="+vm
        print cmd
        os.system(cmd)
        
    for i in range(0,len(vmoutput)-1):
        (vm,uuid) = vmoutput[i].split()
        cmd = run +" pd protect name=testPD_"+vm+" vm-names="+vm
        print cmd
        os.system(cmd)

    cmd = run +" pd list | grep \"Protection Domain\""
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    for i in range(1,len(output)-1):
        (tmp,pd) = output[i].split(":")
        cmd = run +" pd clear-schedules name="+pd.strip()
        print cmd
        os.system(cmd)
        time = 60
        for j in range (1):
            #pd add-hourly-schedule every-nth-hour=1 local-retention=30 name=
            #pd add-minutely-schedule name=testPD_long_run_vm_test23 local-retention-type=DAYS every-nth-minute=10
            cmd = run +" pd add-hourly-schedule name="+pd.strip()+" local-retention=60 every-nth-hour=1"
            print cmd
            os.system(cmd)

        #pd ls-schedules
        for j in range (1):
            #pd add-minutely-schedule name=testPD1 every-nth-minute=1
            cmd = run +" pd ls-schedules name="+pd.strip()+" | grep Id" 
            print cmd
            (tmp,sid) = (os.popen(cmd).read()).split(":")
            #pd set-retention-policy name=testPD_long_run_vm_test25 local-retention=10 id=50e76f42-5e3b-4f9a-a1f4-66e9e0c0f10c
            cmd = run + " pd set-retention-policy name="+pd.strip()+" local-retention="+str(nosnap)+" id="+sid.strip()
            print cmd 
            os.system(cmd)


def delVmbyPattern(cvm,vname):
    ssh = "ssh "+cvm+" -l nutanix"
    acli = " /usr/local/nutanix/bin/acli -y "
    run = ssh +acli+" vm.list"+" | grep \""+vname+"\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(1,len(output)-1):
        #VM name  VM UUID
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        (vm,uuid) = output[i].split()
        cmd = ssh+acli+" vm.delete "+uuid
        print cmd
        os.system(cmd)
        ncli = " /home/nutanix/prism/cli/ncli "
        runs = ssh +ncli
        cmd = runs +"pd clear-schedules name=testPD_"+vm
        print cmd
        os.system(cmd)
        cmd = runs + " pd rm-snap name=testPD_"+vm+" clear-all=true "
        print cmd
        os.system(cmd)
        cmd = runs +" pd unprotect name=testPD_"+vm+" vm-names="+vm
        print cmd
        os.system(cmd)
        cmd = runs + " pd remove name=testPD_"+vm
        print cmd
        os.system(cmd)


def pdRestore(ssh,ncli,acli,cvm,start,off,out,wait,pre,inplace):
    print "start the restore range "+str(start) +" off "+str(off)
    run = ssh+ncli 
    i = 0
    while i < off:
        if out[start]:
            (tmp,pd) = out[start].split(":")
            cmd = run + " pd ls-snaps name="+pd.strip()+" | grep Id | grep -v \"VM Id\""
            print cmd
            snapshots = (os.popen(cmd).read()).split('\n')
            while not snapshots.pop():
                snap = snapshots.pop()
                print "The snapshot --> "+snap
            if snap:
                (tmp,sid) = snap.split(":")
                #cmd = run + " pd restore-snapshot name="+pd.strip()+" snap-ids="+sid.strip()+" vm-name-prefix=cl"+sid.strip()+" vg-name-prefix=cl"+sid.strip()
                if inplace:
                    cmd = run + " pd restore-snapshot name="+pd.strip()+" snap-id="+sid.strip()
                    print cmd 
                else :
                    cmd = run + " pd restore-snapshot name="+pd.strip()+" snap-id="+sid.strip()+" vm-name-prefix="+pre+"_"+" vg-name-prefix="+pre+"_"
                    print cmd 

                os.system(cmd)
                #pd list-snapshots name=testPD_long_run_vm_test10 snap-id=174598
                cmd = run + " pd list-snapshots name="+pd.strip()+" snap-id="+sid.strip()+" | grep \"VM Name\""
                print cmd 
                op = (os.popen(cmd).read())
                if op:
                    vm = op.split(':')[1]
                    time.sleep(60)
                    print "The test Vm "+vm
                    cmd = ssh+acli+ " vm.on "+pre+"_*"+vm.strip()
                    print cmd
                    os.system(cmd)
                    pdCreate(ssh+ncli,pre+"_"+vm.strip(),"5","")
                    time.sleep(wait)
            print "start "+str(start)+" i "+str(i) +" pol "+out[start]
        start = start+1
        i=i+1
    delVmbyPattern(cvm,pre)

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    pat = 'testPD'
    pre = 'test'
    inplace = 0

    try:
        opts, args = getopt.getopt(argv,"hc:p:r:i:",["cvm=","pat=","pre=","inp="])
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
        elif opt in ("-r", "--pre"):
            pre = arg
        elif opt in ("-i", "--inp"):
            inplace = int(arg)

    sshCopyid(cvm)


    while 1:
        runS(cvm,pat,pre,inplace)

def runS(cvm,pat,pre,inplace):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    threads = []
    wait = 3660

    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    for  svmip in svmips:
        sshCopyid(svmip)

    start =0

    #cmd = ssh +ncli+" pd list | grep \"Protection Domain\""
    cmd = ssh +ncli +"pd list | grep -v testVG | grep \"Protection Domain\" | grep -i \""+pat+"\""
    print cmd
    out = (os.popen(cmd).read()).split('\n')
    off = len(out)/len(svmips)
    random.shuffle(out)

    for svmip in svmips:
        ssh = "ssh "+svmip+" -l "+userid
        t = threading.Thread(target=pdRestore, args=(ssh,ncli,acli,svmip,start,off,out,wait,pre,inplace))
        start = start+off
        threads.append(t)

    for x in threads:
        x.start()

    for x in threads:
        x.join()
   
    delVmbyPattern(cvm,pre)

if __name__ == "__main__":
    main(sys.argv[1:])


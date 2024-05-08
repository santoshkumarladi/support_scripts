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

def pdCreate(run,cvm,snap,nosnap,remote):
    (vm,uuid) = snap.split()
    cmd = run +" pd create name=testPD_"+vm
    print cmd
    os.system(cmd) 
    cmd = run +" pd protect name=testPD_"+vm+" vm-ids="+uuid+" cg-name=testCG"+vm
    print cmd
    os.system(cmd) 


    cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
    print cmd
    os.system(cmd)
    cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" every-nth-hour=6 start-time=\\\"02/14/2018 18:30:00 UTC\\\"\""
    print cmd
    os.system(cmd)
    cmd = run +"\" pd add-daily-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" start-time=\\\"02/14/2018 09:30:00 UTC\\\"\""
    print cmd
    os.system(cmd)

    """
    time = 60
    cmd = run +"\" pd add-minutely-schedule name=testPD_"+vm+" every-nth-minute="+str(time)+" start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
    print cmd
    os.system(cmd)
    cmd = run +" pd ls-schedules name=testPD_"+vm+" | grep Id"
    print cmd
    op = os.popen(cmd).read()
    print op

    if op:
        (tmp,sid) = op.split(":")
        #pd set-retention-policy id=93b9428d-20f3-4f2b-ba18-ba8fca53be75 name=testPD_long_run_vm_test35 remote-retention=KEMAK:20 local-retention=20
        cmd = run + " pd set-retention-policy name=testPD_"+vm+" local-retention="+str(nosnap)+" id="+sid.strip()
        print cmd
        os.system(cmd)
        #cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" remote-retention="+remote+":"+str(nosnap)+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
        #print cmd
        #os.system(cmd)
        cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" every-nth-hour=6 start-time=\\\"02/14/2018 18:30:00 UTC\\\"\""
        print cmd
        os.system(cmd)
        cmd = run +"\" pd add-daily-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" start-time=\\\"02/14/2018 09:30:00 UTC\\\"\""
        print cmd
        os.system(cmd)
    time = 60
    for j in range (1):
        #pd add-minutely-schedule name=testPD1 every-nth-minute=1
        time = time+30
    """

def pdUpdate(ssh,ncli,acli,cvm,pat,nosnap,remote):
    run = ssh+ncli
    cmd = ssh +acli+" vm.list | grep -v \"VM name\" | grep "+pat
    print cmd
    vmoutput = (os.popen(cmd).read()).split('\n')
    """
    for i in range(0,len(vmoutput)-1):
        (vm,uuid) = vmoutput[i].split()
        cmd = run +" pd create name=testPD_"+vm
        print cmd
        os.system(cmd) 
        cmd = run +" pd unprotect name=testPD_"+vm+" vm-names="+vm
        print cmd
        os.system(cmd)
    for i in range(0,len(vmoutput)-1):
        (vm,uuid) = vmoutput[i].split()
        cmd = run +" pd protect name=testPD_"+vm+" vm-names="+vm
        print cmd
        os.system(cmd)
    """
    cmd = run +" pd list | grep \"Protection Domain\" | grep "+pat
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
            if remote:
                cmd = run +"\" pd add-hourly-schedule name="+pd.strip()+" local-retention=8 remote-retention="+remote+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
                print cmd
            else:
                cmd = run +"\" pd add-hourly-schedule name="+pd.strip()+" local-retention=8 every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
                print cmd
            os.system(cmd)
            cmd = run +"\" pd add-hourly-schedule name="+pd.strip()+" local-retention=10 every-nth-hour=6 start-time=\\\"02/14/2018 18:30:00 UTC\\\"\""
            print cmd
            os.system(cmd)
            cmd = run +"\" pd add-daily-schedule name="+pd.strip()+" local-retention=5 start-time=\\\"02/14/2018 09:30:00 UTC\\\"\""
            print cmd
            os.system(cmd)
        """
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
        """
def pdAddDr(ssh,ncli,acli,cvm,remote,pat,nosnap):
    run = ssh+ncli
    cmd = run +" pd list | grep \"Protection Domain\" | grep "+pat 
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    for i in range(1,len(output)-1):
        (tmp,pd) = output[i].split(":")
        #pd add-minutely-schedule name=testPD1 every-nth-minute=1
        cmd = run +" pd ls-schedules name="+pd.strip()+" | grep Id" 
        print cmd
        op = os.popen(cmd).read()
        print op

        if op:
            (tmp,sid) = op.split(":")
            #pd set-retention-policy id=93b9428d-20f3-4f2b-ba18-ba8fca53be75 name=testPD_long_run_vm_test35 remote-retention=KEMAK:20 local-retention=20
            cmd = run + " pd set-retention-policy name="+pd.strip()+" local-retention="+str(nosnap)+" id="+sid.strip()+" remote-retention="+remote+":"+str(nosnap)
            print cmd 
            os.system(cmd)

def pdDelSnaps(run,cvm,start,off,out):
    print "start the delete on range "+str(start) +" off "+str(off)
    i = 0
    while i < off:
        if out[start]:
            (tmp,pd) = out[start].split(":")
            cmd = run +"pd clear-schedules name="+pd.strip()
            print cmd

def pdDelSnap(run,cvm,start,off,out):
    print "start the delete on range "+str(start) +" off "+str(off)
    i = 0
    while i < off:
        if out[start]:
            (tmp,pd) = out[start].split(":")
            cmd = run +"pd clear-schedules name="+pd.strip()
            print cmd
            os.system(cmd)
            """    
            cmd = run + " pd ls-snaps name="+pd.strip()+" | grep id"
            print cmd
            snapshots = (os.popen(cmd).read()).split('\n')
            for i in range(0,len(snapshots)-1):
                (tmp,sid) = snapshots[i].split(":")
                cmd = run + " pd rm-snapshot name="+pd.strip()+" snap-ids="+sid.strip()
                print cmd 
                os.system(cmd)
            """
            cmd = run + " pd rm-snap name="+pd.strip()+" clear-all=true "
            print cmd 
            os.system(cmd)
            start = start+1
            cmd = run + " pd remove name="+pd.strip()
            os.system(cmd)
            print cmd

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    pat = 'long'
    remote=''

    try:
        opts, args = getopt.getopt(argv,"hc:p:r:",["cvm=","pat=","remote="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -p <pattern> -r <remote>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--pat"):
            pat = arg
        elif opt in ("-r", "--remote"):
            remote = arg

    sshCopyid(cvm)



    runS(cvm,pat,remote)

def runS(cvm,pat,remote):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
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

    start =2
    #cmd = ssh +ncli+" pd list | grep \"Protection Domain\""
    cmd = ssh +ncli +"pd list | grep \"Protection Domain\" | grep \""+pat+"\""
    print cmd
    out = (os.popen(cmd).read()).split('\n')
    off = len(out)/len(svmips)
    pdUpdate(ssh,ncli,acli,cvm,pat,30,remote)

    """
    for svmip in svmips:
        ssh = "ssh "+svmip+" -l "+userid
        t = threading.Thread(target=pdDelSnap, args=(ssh+ncli,svmip,start,off,out,))
        start = start+off
        threads.append(t)

    for x in threads:
        x.start()

    for x in threads:
        x.join()
    #remote="auto_cluster_prod_gurunath_gudi_1a4c240d10be"
    #run = ssh +acli+" vm.list | grep "+pat
    run = ssh +acli+" vm.list | grep -v Backup | grep -v "+pat
    print run
    output = (os.popen(run).read()).split('\n')
    remote = "norcross:10"
    #for i in range(1,len(output)-1):
    #    pdCreate(ssh+ncli,cvm,output[i],4,remote)
    #pdAddDr(ssh,ncli,acli,cvm,remote,pat,30)
    #pdDelSnap(ssh,cvm)
    """

if __name__ == "__main__":
    main(sys.argv[1:])


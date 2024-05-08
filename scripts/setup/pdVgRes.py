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

def pdCreate(ssh,run,vm):
    try:
        time.sleep(30)
        nosnap = 10
        cmd = ssh+" vg.list | grep "+vm
        print cmd
        uuid  = (os.popen(cmd).read()).split()[1]
        cmd = run +" pd create name=testPD_"+vm
        print cmd
        os.system(cmd)
        cmd = run +" pd protect name=testPD_"+vm+" volume-group-uuids="+uuid+" cg-name="+vm
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
    except Exception as e:
        print "Error --> "


def vgDel(ssh,ncli,vgList):
    print "Delete VG ---> "
    try:
        for vg in vgList:
            cmd = ncli+ " pd ls name="+vg+ " | grep \"Volume Group Uuid\""
            uuid= (os.popen(cmd).read()).split(':')[1].strip()
            cmd = ssh+" vg.get "+vg+" | grep \"external_initiator_name\""
            print cmd
            op = os.popen(cmd).read()
            if op:
                init = op.split('"')[1].strip()
                cmd = ssh+" vg.detach_external "+vg+" initiator_name="+init
                print cmd
                os.system(cmd)
            cmd = ssh+" vg.delete "+vg
            print cmd
            os.system(cmd)
            cmd = ncli +"pd clear-schedules name=testPD_"+vg
            print cmd
            os.system(cmd)
            cmd = ncli + " pd rm-snap name=testPD_"+vg+" clear-all=true "
            print cmd
            os.system(cmd)
            cmd = ncli +" pd unprotect name=testPD_"+vg+" volume-group-uuids="+uuid
            print cmd
            os.system(cmd)
            cmd = ncli + " pd remove name=testPD_"+vg
            print cmd
            os.system(cmd)
    except Exception as e:
        print "Error --> "

def cleanUp(ssh,ncl,dest,pat):
    ncli = ssh+ncl
    acli = " /usr/local/nutanix/bin/acli -y"
    cmd = "ssh "+dest+" -l nutanix "+acli+" vm.delete *"+pat+"*"
    print cmd
    os.system(cmd)
    cmd = ssh+acli+" vg.list | grep "+pat
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    for i in range(0,len(output)-1):
        (vg,uuid) = output[i].split()
        cmd = ssh+acli+" vg.get "+vg+" | grep \"external_initiator_name\""
        print cmd
        op = os.popen(cmd).read()
        if op:
            init = op.split('"')[1].strip()
            cmd = ssh+acli+" vg.detach_external "+vg+" initiator_name="+init
            print cmd
            os.system(cmd)
        cmd = ssh+acli+" vg.delete "+vg
        print cmd
        os.system(cmd)
        try:
            cmd = ncli +"pd clear-schedules name=testPD_"+vg
            print cmd
            os.system(cmd)
            cmd = ncli + " pd rm-snap name=testPD_"+vg+" clear-all=true "
            print cmd
            os.system(cmd)
            cmd = ncli +" pd unprotect name=testPD_"+vg+" volume-group-uuids="+uuid
            print cmd
            os.system(cmd)
            cmd = ncli + " pd remove name=testPD_"+vg
            print cmd
            os.system(cmd)
        except Exception as e:
            print "Error --> "

#ssh,ncli,acli,svmip,start,off,out,wait,pre,fsize,dest,nodisk,vgcount,vdsize
def pdRestore(ssh,ncli,acli,cvm,start,off,out,wait,pre,fsize,dest,nodisk,vgcount,vdsize):
    print "start the restore range "+str(start) +" off "+str(off)
    vgList=[]
    run = ssh+ncli 
    i = 0
    try :
        while i < off:
            if out[start]:
                (tmp,pd) = out[start].split(":")
                cmd = run + " pd ls-snaps name="+pd.strip()+" | grep Id | grep -v \"VM Id\""
                print cmd
                snapshots = (os.popen(cmd).read()).split('\n')
                if len(snapshots) > 1:
                    while not snapshots.pop():
                        snap = snapshots.pop()
                        print "The snapshot --> "+snap
                    if snap:
                        (tmp,sid) = snap.split(":")
                        cmd = run + " pd restore-snapshot name="+pd.strip()+" snap-id="+sid.strip()+" vg-name-prefix="+pre+"_"
                        print cmd 
                        os.system(cmd)
                        time.sleep(60)
                        cmd =run + " pd ls name="+pd.strip()+ " | grep \"Consistency Group\""
                        vg  = (os.popen(cmd).read()).split(':')[1].strip()
                        pdCreate(ssh+acli,run,pre+"_"+vg)
                        cmd = "/home/santoshkumar.ladi/scripts/setup/vgStress.py -c "+cvm+ " -g "+pre+"_"+vg+" -l "+dest+" -p "+pre+" -f "+fsize+" -d "+vdsize+" -r 0 -w "+str(wait)+" &"
                        print cmd 
                        os.system(cmd)
                        vgList.append(vg)
                    print "start "+str(start)+" i "+str(i) +" pol "+out[start]
            start = start+1
            i=i+1
    except Exception as e:
        print "Error --> "
        
    vgDel(ssh+acli,run,vgList)
    time.sleep(wait)

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    pat = 'testVG'
    pre = 'last'
    dest = ''
    nodisk = 50
    vgcount = 10
    vdsize = '50G'
    fsize = '2T'
    wait = 3600
    userid = 'nutanix'
    image = 'vgcS'
    container = "long_test_cont_1,long_test_cont_2,long_test_cont_3,long_test_cont_4"

    try:
        opts, args = getopt.getopt(argv,"hc:p:r:l:n:v:d:f:w:",["cvm=","pat=","pre=","iscsi=","vdsize=","nodisk=","vgcount=","fsize=","wait="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -p <pat> -r <prepend the pat> -l <dest cluster> -n <no of disk> -d <vdisk size> -v <vg count> -f <fs size> -w <wait>'
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--pat"):
            pat = arg
        elif opt in ("-r", "--pre"):
            pre = arg
        elif opt in ("-l", "--iscsi"):
            dest = arg
        elif opt in ("-n", "--nodisk"):
            nodisk = int(arg)
        elif opt in ("-v", "--vgcount"):
            vgcount = int(arg)
        elif opt in ("-d", "--vdsize"):
            vdsize = arg
        elif opt in ("-f", "--fsize"):
            fsize = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm)


    while 1:
        runS(cvm,pat,pre,fsize,dest,nodisk,vgcount,vdsize)

def runS(cvm,pat,pre,fsize,dest,nodisk,vgcount,vdsize):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    threads = []
    wait = 3660

    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    #cleanUp(ssh,ncli,dest,pre)
    #sys.exit()
    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    for  svmip in svmips:
        sshCopyid(svmip)

    start =0

    #cmd = ssh +ncli+" pd list | grep \"Protection Domain\""
    cmd = ssh +ncli +"pd list | grep \"Protection Domain\" | grep \""+pat+"\""
    print cmd
    out = (os.popen(cmd).read()).split('\n')
    total = len(out)
    no = len(svmips)
    off = total//no
    print "off "+str(off)+" out "+str(len(out))+" svmips "+str(len(svmips))
    random.shuffle(out)

    for svmip in svmips:
        ssh = "ssh "+svmip+" -l "+userid
        t = threading.Thread(target=pdRestore, args=(ssh,ncli,acli,svmip,start,off,out,wait,pre,fsize,dest,nodisk,vgcount,vdsize))
        time.sleep(60)
        start = start+off+1
        threads.append(t)

    for x in threads:
        x.start()

    for x in threads:
        x.join()
   

if __name__ == "__main__":
    main(sys.argv[1:])


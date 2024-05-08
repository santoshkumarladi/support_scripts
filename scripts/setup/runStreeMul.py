#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import threading
import pexpect

outlock = threading.Lock()

def delSnapshot(ssh,vm):
    cmd = ssh+" vm.snapshot_list "+vm
    snapshots = (os.popen(cmd).read()).split('\n')
    for i in range(2,len(snapshots)-1):
    #Snapshot name  Snapshot UUID
        (snapshot,uuid) = snapshots[i].split()
        dels = " snapshot.delete "+snapshot+":"+uuid
        run = ssh+dels  
        print run
        os.system(run)

def createSnapshot (ssh,vm,count,wait):
    print 'Create snaphot  '
    for i in range(count):
        snapname = "testSnap"+str(random.randint(100,128908))
        cmd = " vm.snapshot_create "+vm+" snapshot_name_list="+snapname
        run = ssh+cmd
        print run
        os.system(run)
        time.sleep(wait)

def createNestedClone(ssh,clone_from_vm,count,vmclone):
    for i in range(count):
        clone_name = clone_from_vm+"clone"+str(random.randint(100,128908))
        cmd = ssh+ " vm.clone " +clone_name+" clone_from_vm=" + clone_from_vm
        print cmd
        os.system(cmd)
        vmclone.append(clone_name)
        clone_from_vm = clone_name
    return vmclone

def vmcloneOpt(ssh,clvm):
    cmd = ssh+ " vm.on " +clvm
    print cmd
    os.system(cmd)
    cmd = ssh+ " vm.power_cycle " +clvm
    print cmd
    os.system(cmd)
    cmd = ssh+ " vm.delete " +clvm
    print cmd
    os.system(cmd)

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
            
def vmCreateDelete(ssh,count,wait,vm):
    vmlist = []
    vmclone = []
    for i in range(count):
        vmname = "testVM"+str(random.randint(100,128908))
        cmd = ssh+" vm.create "+vmname
        print cmd
        os.system(cmd)
        #time.sleep(wait)
        vmlist.append(vmname)
       
    createNestedClone(ssh,vm,count,vmclone)

    for clvm in vmclone:
        vmcloneOpt(ssh,clvm)

    for vmname  in (vmlist):
        cmd = ssh+" vm.delete "+vmname
        print cmd
        os.system(cmd)
        #time.sleep(wait)


def killS(wait):
    time.sleep(wait)
    cmd = "kill $(ps aux | grep 'compTest.py' | awk '{print $2}')"
    os.system(cmd)

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    cvm = ''
    wait = 0
    cmd  = 0
    b=d=2
    dcount=7
    dsize="200G"
    cmd=1
    wait=7200
    mntp = "/mnt/dataMnt"
    con = "long_test_cont_1" 
    try:
        opts, args = getopt.getopt(argv,"hi:b:d:c:m:n:s:r:w:",["cvm=","b=","d=","con=","mntp=","ndrive=","dsize=","cmd=","wait="])
    except getopt.GetoptError:
        print 'runStreeMul.py -i <cvm> -v <vname> -b <breadth> -d <depth> -c <con> -m <mntp> -n <nodrive> -s <dsize> -w <wait> -r <all>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'runStreeMul.py -i <cvm> -v <vname> -b <breadth> -d <depth> -c <con> -m <mntp> -n <nodrive> -s <dsize> -w <wait> -r <all>'
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvm = arg
        elif opt in ("-b", "--breadth"):
            b = int(arg)
        elif opt in ("-d", "--depth"):
            d = int(arg)
        elif opt in ("-c", "--con"):
            con = arg
        elif opt in ("-n", "--ndrive"):
            dcount = int(arg)
        elif opt in ("-s", "--dsize"):
            dsize = arg
        elif opt in ("-m", "--mntp"):
            mntp = arg
        elif opt in ("-r", "--cmd"):
            cmd  = int(arg)
        elif opt in ("-w", "--wait"):
            wait  = int(arg)

    sshCopyid(cvm)
    if not wait:
        print "Wait -> "+str(wait)
        wait = 240000
    tc = 0
    while 1:
        print "Wait -> "+str(wait)
        runS(cvm,mntp,cmd,userid,passwd,tc,con,dcount,dsize,b,d)
        killS(wait)
        tc = tc+1

def copyTheScript(ip):
    passwd="Srinidhi@2012"
    try :
        cmd = "sudo scp -r /home/santoshkumar.ladi/scripts nutanix@"+ip+":/home/nutanix"
        print cmd
        child = pexpect.spawn(cmd)
        r=child.expect ('assword:')
        print r
        if r==0:
            child.sendline (passwd)
        child.interact()
        child.close()
    except Exception as e:
        print "Oops Something went wrong buddy"
        #print e

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

def vmAddDisk(ssh,vname,container,dcount,dsize):
    cmd = ssh+" vm.disk_list "+vname
    output = (os.popen(cmd).read()).split('\n')
    if len(output) > 3:
        for i in range(3,len(output)):
            cmd = ssh+" vm.disk_delete "+vname+" disk_addr=scsi."+str(i)
            print cmd
            os.system(cmd)

    for i in range(dcount):
        cmd = ssh+" vm.disk_create "+vname+" container="+container+ " create_size="+dsize
        print cmd
        os.system(cmd)


def runTheScript(ip,uuid,mntp,userid,passwd,b,d,opt,alls):
    #sudo runTest.py -v <vname> -b <breadth> -d<depth> -c<con> -m <mntp> -n <nodrive> -s <disk size>
    run = "ssh "+ip+" -l "+userid+" \"sudo /home/nutanix/scripts/setup/compTest.py -m " +mntp+ " -b "+str(b)+" -d "+str(d)+" -s "+str(opt)+" -a "+str(alls)+" </dev/null>/dev/null 2>&1 &\""
    print run
    os.system(run)


def runS(cvm,mntp,alls,userid,passwd,tc,con,dcount,dsize,b,d):
    vmlist = []
    wait = 10
    count = 2
    opt = 1
    threads = []

    #ssh 10.46.32.65 -l nutanix ls
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y "
    ncli = " /home/nutanix/prism/cli/ncli "

    delVmbyPattern(ssh + acli,"clone")

    run = ssh +acli+" vm.list | grep -v \"gold\" | grep -v \"fio\" | grep -v \"windows\" | grep -v \"time\" | grep -v \"VM name\" "
    print run
    output = (os.popen(run).read()).split('\n')
    print output
    random.shuffle(output)
    for i in range(len(output)-1):
        #VM name  VM UUID                               
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        if output[i]:
            (vm,uuid) = output[i].split()
            run = ssh +ncli+" vm list name="+vm+" | grep \"VM IP Addresses\""
            print run
            #    VM IP Addresses           : 10.46.141.186
            match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
            if match is not None:
                ip = match.group()
                print vm+" "+uuid+" "+ip
                vmlist.append({'uuid':uuid,'vm':vm,'ip':ip})
                sshCopyid(ip)
                #run = ssh +acli+" vm.power_cycle "+vm
                #print run
                #os.system(run)
                #time.sleep(60)
                cmd = "ssh "+ip+" -l nutanix \" rm -rf /home/nutanix/scripts ; sudo rm -rf /home/nutanix/data/cores/* \""
                print cmd
                os.system(cmd)
                cmd = "scp -r /home/santoshkumar.ladi/scripts nutanix@"+ip+":/home/nutanix"
                print cmd
                os.system(cmd)
                cmd = "ssh "+ip+" -l nutanix \"/home/nutanix/scripts/setup/killScript.py dataMnt \""
                print cmd
                os.system(cmd)
                cmd = "ssh "+ip+" -l nutanix \" sudo rm -rf /mnt/dataMnt/* \""
                print cmd
                os.system(cmd)
                #vmAddDisk(ssh+acli,uuid,con,dcount,dsize)
                runTheScript(ip,uuid,mntp,userid,passwd,b,d,opt,alls)
                if opt == 4:
                    opt = 1
                else :
                    opt = opt+1
 
        """
        Ssh = ssh+acli
        t = threading.Thread(target=createSnapshot, args=(Ssh,vm,count,wait,))
        threads.append(t)
        t = threading.Thread(target=delSnapshot, args=(Ssh,vm,))
        threads.append(t)
        t = threading.Thread(target=vmCreateDelete, args=(Ssh,count,wait,vm,))
        threads.append(t)


    for x in threads: 
        x.start()
        time.sleep(5)

    for x in threads: 
        x.join()
    """

if __name__ == "__main__":
    main(sys.argv[1:])


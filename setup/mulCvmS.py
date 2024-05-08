#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import threading

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
        
def vmCreateDelete(ssh,count,wait):
    vmlist = []
    for i in range(count):
        vmname = "testVM"+str(random.randint(100,128908))
        cmd = ssh+" vm.create "+vmname
        print cmd
        os.system(cmd)
        time.sleep(wait)
        vmlist.append(vmname)
    for vmname  in (vmlist):
        cmd = ssh+" vm.delete "+vmname
        print cmd
        os.system(cmd)
        time.sleep(wait)
    



def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    try:
        opts, args = getopt.getopt(argv,"hc:r:",["cvm=","cmd="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -r <cmd> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -r <cmd> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-r", "--cmd"):
            cmd = arg
    runS(cvm,userid,passwd)


def runS(cvm,userid,passwd):
    vmlist = {}
    wait = 10
    count = 10
    threads = []
    #ssh 10.46.32.65 -l nutanix ls
    ssh = "ssh "+cvm+" -l "+userid+" /usr/local/nutanix/bin/acli -y"

    run = ssh +" vm.list"
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(2,len(output)-1):
        #VM name  VM UUID                               
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        #print output[i]
        (vm,uuid) = output[i].split()
        (vmlist[vm]) = uuid
        t = threading.Thread(target=createSnapshot, args=(ssh,vm,count,wait,))
        threads.append(t)
        t = threading.Thread(target=delSnapshot, args=(ssh,vm,))
        threads.append(t)

    t = threading.Thread(target=vmCreateDelete, args=(ssh,count,wait,))
    threads.append(t)

    for x in threads: 
        x.start()
        time.sleep(5)

    for x in threads: 
        x.join()


if __name__ == "__main__":
    while 1:
        main(sys.argv[1:])


#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import paramiko
import time
import threading

outlock = threading.Lock()

def execute(ssh,cvm,userid,passwd,cmd):
    ssh.connect(cvm, port=22, username=userid, password=passwd)
    run = "/usr/local/nutanix/bin/acli -y "+cmd  
    print run
    with outlock:
        stdin, stdout, stderr = ssh.exec_command(run)
        #print 'stdout ' +stdout+ 'stdin ' +stdin+ 'stderr ' +stderr 
        string = stdout.read().decode('ascii').strip("\n")
    stdin.close()
    ssh.close()
    return string

def delSnapshot(cvm,userid,passwd,vmlist):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(cvm, port=22, username=userid, password=passwd)
    for vm in vmlist.keys():
        cmd = "vm.snapshot_list "+vm
        snapshots = execute(ssh,cvm,userid,passwd,cmd)
        #Snapshot name  Snapshot UUID
        for line in snapshots.split('\n') :
            match = re.match(r"Snapshot\s+name\s+Snapshot\s+UUID",line,re.I)
            if match is None :
                (snapshot,uuid) = line.split()
                print snapshot
                dels = "snapshot.delete "+snapshot+":"+uuid
                run = "/usr/local/nutanix/bin/acli -y "+dels  
                #execute(ssh,cvm,userid,passwd,dels)
                stdin, stdout, stderr = ssh.exec_command(run)
                string = stdout.read().decode('ascii').strip("\n")

def createSnapshot (cvm,userid,passwd,vmlist,count,wait):
    print 'Create snaphot on cvm -> ',cvm
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(cvm, port=22, username=userid, password=passwd)
    for vm in vmlist.keys():
        for i in range(count):
            snapname = "testSnap"+str(random.randint(100,128908))
            cmd = "vm.snapshot_create "+vm+" snapshot_name_list="+snapname
            print cmd
            #execute(ssh,cvm,userid,passwd,cmd)
            run = "/usr/local/nutanix/bin/acli -y "+cmd
            stdin, stdout, stderr = ssh.exec_command(run)
            string = stdout.read().decode('ascii').strip("\n")
            time.sleep(wait)
        
def vmCreateDelete(ssh,cvm,userid,passwd,count,wait):
    vmlist = []
    #ssh.connect(cvm, port=22, username=userid, password=passwd)
    for i in range(count):
        vmname = "testVM"+str(random.randint(100,128908))
        cmd = "vm.create "+vmname
        execute(ssh,cvm,userid,passwd,cmd)
        time.sleep(wait)
        vmlist.append(vmname)
    for vmname  in (vmlist):
        cmd = "vm.delete "+vmname
        execute(ssh,cvm,userid,passwd,cmd)
        time.sleep(wait)
    #ssh.close()
    



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

    ssh = paramiko.SSHClient()
    #ssh.load_system_host_keys()
    paramiko.util.log_to_file("filename.log")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(cvm, port=22, username=userid, password=passwd,timeout=120)

    time.sleep(5)

    print('connected')

    run = "/usr/local/nutanix/bin/acli -y vm.list"
    stdin, stdout, stderr = ssh.exec_command(run)
    output = stdout.read().decode('ascii').strip("\n")
    #output = execute(ssh,cvm,userid,passwd,"vm.list ")
    for line in output.split('\n') :
        #VM name  VM UUID                               
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        match = re.match(r"VM\s+name\s+VM\s+UUID",line,re.I)
        if match is None :
            (vm,uuid) = line.split()
            (vmlist[vm]) = uuid
    stdin.close()
    ssh.close()
    
    t = threading.Thread(target=createSnapshot, args=(cvm,userid,passwd,vmlist,count,wait,))
    threads.append(t)
    t = threading.Thread(target=delSnapshot, args=(cvm,userid,passwd,vmlist,))
    threads.append(t)
    #t = threading.Thread(target=vmCreateDelete, args=(ssh,cvm,userid,passwd,count,wait,))
    #threads.append(t)

    for x in threads: 
        x.start()
        time.sleep(5)

    for x in threads: 
        x.join()
    #createSnapshot(ssh,cvm,userid,passwd,vmlist,count,wait)    
        #delSnapshot(ssh,cvm,userid,passwd,vmlist)    

    ssh.close()

if __name__ == "__main__":
    main(sys.argv[1:])


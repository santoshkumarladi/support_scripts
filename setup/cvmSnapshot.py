#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import paramiko
import time

def execute(ssh,cvm,userid,passwd,cmd):
    ssh.connect(cvm, port=22, username=userid, password=passwd)
    run = "/usr/local/nutanix/bin/acli -y "+cmd  
    print run
    stdin, stdout, stderr = ssh.exec_command(run)
    #print 'stdout ' +stdout+ 'stdin ' +stdin+ 'stderr ' +stderr 
    string = stdout.read().decode('ascii').strip("\n")
    ssh.close()
    return string

def delSnapshot(ssh,cvm,userid,passwd,vmlist):
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
                execute(ssh,cvm,userid,passwd,dels)
    ssh.close()

def createSnapshot (ssh,cvm,userid,passwd,vmlist,count,wait):
    ssh.connect(cvm, port=22, username=userid, password=passwd)
    for vm in vmlist.keys():
        for i in range(count):
            snapname = "testSnap"+str(random.randint(100,128908))
            cmd = "vm.snapshot_create "+vm+" snapshot_name_list="+snapname
            execute(ssh,cvm,userid,passwd,cmd)
            time.sleep(wait)
        



def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    vmlist = {}
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

    ssh = paramiko.SSHClient()
    #ssh.load_system_host_keys()
    paramiko.util.log_to_file("filename.log")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(cvm, port=22, username=userid, password=passwd)

    time.sleep(5)
    print('connected')
    output = execute(ssh,cvm,userid,passwd,"vm.list ")
    for line in output.split('\n') :
        #VM name  VM UUID                               
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        match = re.match(r"VM\s+name\s+VM\s+UUID",line,re.I)
        if match is None :
            (vm,uuid) = line.split()
            (vmlist[vm]) = uuid
    ssh.close()
    
    wait = 10
    count = 10
    while 1 :    
        createSnapshot(ssh,cvm,userid,passwd,vmlist,count,wait)    
        delSnapshot(ssh,cvm,userid,passwd,vmlist)    


if __name__ == "__main__":
    main(sys.argv[1:])


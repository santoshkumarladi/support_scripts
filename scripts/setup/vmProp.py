#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import threading


def vmCreate(ssh,hostlist,patr):
    run = ssh +" vm.list"+" | grep \""+patr+"\""
    #run = ssh +" vm.list"
    print run+" host list "+str(hostlist)
    output = (os.popen(run).read()).split('\n')
    pernode = len(output)//len(hostlist) 
    print "pernode --> "+str(pernode) +" Host len -> "+str(len(hostlist))+" no of vms -> "+str(len(output))
    """
    for i in range(1,len(output)-1):
        vm.nic_get long_run_vm_fioStress1 | grep mac_addr
        cmd = ssh+" vm.nic_get "+vm+" | grep mac_addr"
        macs = (os.popen(cmd).read()).split('\n')
        print macs
        for mac in macs:
            if mac:
                mac = mac.split()[1].replace('"', '') 
                cmd = ssh+" vm.nic_delete "+vm+" "+mac
                print cmd
                os.system(cmd)

        cmd = ssh+" vm.nic_create "+vm+" network=vlan0"
        print cmd
        os.system(cmd)
    """
    i=0
    for host in hostlist:
       count = 0
       while count < pernode:
           (vm,uuid) = output[i].split()
           cmd = ssh+" vm.affinity_set "+vm+" host_list="+host
           print cmd
           os.system(cmd)
           count = count+1
           if i < len(output):
               i=i+1

def vmAddisk(ssh,containername,edisksize,patr):
    imgp = '/long_test_cont_1/CentOS7.2.img'
    run = ssh +" vm.list"+" | grep \""+patr+"\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(1,len(output)-1):
        (vmname,uuid) = output[i].split()
        cmd = ssh+" vm.disk_create "+vmname+" clone_from_adsf_file="+imgp
        print cmd
        os.system(cmd)
        """
        for i in range(5):
            #vm.disk_create long_run_vm_2 container=long_test_cont_1 create_size=400G
            cmd = ssh+" vm.disk_create "+vmname+" container="+containername+" create_size="+edisksize
            print cmd
            os.system(cmd)
        """

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

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    hostlist = []
    host = ''
    seperator = ','

    try:
        opts, args = getopt.getopt(argv,"hc:p:",["cvm=","pat="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm>  -p <pattern>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm>  -p <pattern>'
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--pat"):
            patr = arg

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid

    acli = " /usr/local/nutanix/bin/acli -y"

    run = ssh+acli+" host.list | grep -v \"Hypervisor\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range (len(output)-1):
        svmips = output[i].split()
        print svmips[0]
        hostlist.append(svmips[0])
    
    #host = seperator.join(hostlist)
    
    vmCreate(ssh+acli,hostlist,patr)
    #vmAddisk(ssh+acli,'long_test_cont_1','100G',patr)

if __name__ == "__main__":
    main(sys.argv[1:])


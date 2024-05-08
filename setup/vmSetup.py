#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import threading


def vmCreate(ssh,cvm,vmcount,bdisksize,vcpus,hostlist,containername,edisksize,imgp,userid,patr):
    vmlist = []
    vmclone = []
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "
    run = ssh+acli
    for i in range (vmcount):
        #vm.create long_run_vm_2 memory=8G num_vcpus=4
        vmname = "long_run_vm_"+patr+str(i)
        cmd = run+ " vm.create "+vmname+" memory="+bdisksize+" num_vcpus="+str(vcpus)
        print cmd
        os.system(cmd)
        #vm.disk_create testVM clone_from_adsf_file=/nutest_ctr_0/nutest/goldimages/ahv/Centos_QOS-1.0/Centos72_QOS.img
        cmd = run+" vm.disk_create "+vmname+" clone_from_adsf_file="+imgp 
        print cmd
        os.system(cmd)
        #vm.nic_create testVM network=vlan0
        cmd =run+ " vm.nic_create "+vmname+" network=vlan0"
        print cmd
        os.system(cmd)
        #vm.affinity_set long_run_vm_2 host_list=10.46.32.121,10.46.32.122
        cmd = run+" vm.affinity_set "+vmname+" host_list="+hostlist
        print cmd
        os.system(cmd)
        cmd = run+" vm.on "+vmname
        print cmd
        os.system(cmd)
        for i in range(8):
            #vm.disk_create long_run_vm_2 container=long_test_cont_1 create_size=400G
            cmd = run+" vm.disk_create "+vmname+" container="+containername+" create_size="+edisksize
            print cmd
            os.system(cmd)
        """
        #pd create name=testPD
        cmd = ssh+ncli +"pd create name=testPD_"+vmname
        print cmd
        os.system(cmd)
        #protect vm-names=testVM1 name=testPD1 ignore-duplicates=true
        cmd = ssh+ncli +"pd protect vm-names="+vmname+" name=testPD_"+vmname+" ignore-duplicates=true"
        print cmd
        os.system(cmd)
        time = 60
        for j in range (1):
            #pd add-minutely-schedule name=testPD1 every-nth-minute=1
            cmd = ssh+ncli +"pd add-minutely-schedule name=testPD_"+vmname+" every-nth-minute="+str(time)
            print cmd
            os.system(cmd)
            time = time+10
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
    patr = ''
    imgp = '/long_test_cont_1/CentOS7.2.img'
    container = 'long_test_cont_1'
    try:
        opts, args = getopt.getopt(argv,"hc:r:m:p:",["cvm=","container=","imgp=","pat="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -r <container> -m <imgp> -p <pattern>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -r <container> -m <imgp> -p <pattern>'
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-r", "--container"):
            container = arg
        elif opt in ("-m", "--imgp"):
            imgp = arg
        elif opt in ("-p", "--pat"):
            patr = arg

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid

    acli = " /usr/local/nutanix/bin/acli -y"

    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    print output[0]
    svmips = output[0].split()
    hostlist =  output[0].replace(" ", ",")

    runS(ssh+acli,cvm,container,imgp,hostlist,patr)

def runS(ssh,cvm,container,imgp,hostlist,patr):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    vcpus = 4
    bdisksize = '8G'
    edisksize = '100G'
    vmcount = 10
    vmCreate(ssh,cvm,vmcount,bdisksize,vcpus,hostlist,container,edisksize,imgp,userid,patr)


if __name__ == "__main__":
    main(sys.argv[1:])


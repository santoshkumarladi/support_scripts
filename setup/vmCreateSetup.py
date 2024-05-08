#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import threading


def delVmbyPattern(ssh,vname):
    run = ssh +" vm.list"+" | grep \""+vname+"\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(1,len(output)-1):
        #VM name  VM UUID
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.delete "+vm
        print cmd
        os.system(cmd)

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

def createNestedClone(ssh,clone_from_vm,count,vmclone):
    for i in range(count):
        clone_name = clone_from_vm+"clone"+str(random.randint(100,128908))
        cmd = ssh+ " vm.clone " +clone_name+" clone_from_vm=" + clone_from_vm
        print cmd 
        os.system(cmd)
        vmclone.append(clone_name)
        clone_from_vm = clone_name
    return vmclone


def vmCreateDelete(ssh,count,wait):
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

def vmMigrate(ssh,vname):
    run = ssh +" vm.list"+" | grep \""+vname+"\""
    print run 
    output = (os.popen(run).read()).split('\n')
    for i in range(1,len(output)-1):
        #vm.migrate long_run_vm_11 live=true
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.migrate "+vm+" live=true"
        print cmd 
        os.system(cmd)

def vmAddDisk(ssh,vname,container):
    run = ssh +" vm.list"+" | grep \""+vname+"\""
    print run 
    output = (os.popen(run).read()).split('\n')
    for i in range(1,len(output)-1):
        #vm.disk_create long_run_vm_2 container=long_test_cont_1 create_size=400G
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.disk_create "+vm+" container="+container+ "create_size=4G"
        print cmd 
        os.system(cmd)

"""
<acropolis> vm.disk_list long_run_vm_1
Device bus  Device index
scsi        0
scsi        1
"""
def vmDelDisk(ssh,vname):
    run = ssh +" vm.list"+" | grep \""+vname+"\""
    print run 
    output = (os.popen(run).read()).split('\n')
    for i in range(1,len(output)-1):
        #vm.disk_create long_run_vm_2 container=long_test_cont_1 create_size=400G
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.disk_list "+vm
        print cmd 
        ou = (os.popen(cmd).read()).split('\n')
        if (len(ou)-1) > 2:
            for i in range(3,len(ou)-1):
                (vm,uuid) = ou[i].split()
                cmd = ssh+" vm.disk_delete "+vm+" disk_addr=scsi."+uuid
                print cmd 
                os.system(cmd)


def vmCreate(ssh,cvm,vmcount,bdisksize,vcpus,hostlist,containername,edisksize,imgp,userid):
    vmlist = []
    vmclone = []
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "
    run = ssh+acli
    j=0

    for i in range (vmcount):
        #vm.create long_run_vm_2 memory=8G num_vcpus=4
        vmname = "long_run_vm_"+str(i)
        cmd = run+ " vm.create "+vmname+" memory="+bdisksize+" num_vcpus="+str(vcpus)
        print cmd
        os.system(cmd)
        #vm.disk_create testVM clone_from_adsf_file=/nutest_ctr_0/nutest/goldimages/ahv/Centos_QOS-1.0/Centos72_QOS.img
        #cmd = run+" vm.disk_create "+vmname+" clone_from_adsf_file="+imgp 
        cmd = run+" vm.disk_create "+vmname+" clone_from_image="+imgp[j] 
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
        #vm.disk_create long_run_vm_2 container=long_test_cont_1 create_size=400G
        cmd = run+" vm.disk_create "+vmname+" container="+containername[j]+" create_size="+edisksize
        print cmd
        os.system(cmd)
        if j <= 2:
            j=0
        else :
            j=j+1
        

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
    cmd = ''
    imgp = '/long_test_cont_1/CentOS7.2.img'
    container = 'long_test_cont_1'
    try:
        opts, args = getopt.getopt(argv,"hc:r:m:",["cvm=","container=","imgp="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -r <container> -m <imgp>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -r <container> -m <imgp>'
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-r", "--container"):
            container = arg
        elif opt in ("-m", "--imgp"):
            imgp = arg

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    print output[0]
    svmips = output[0].split()
    for  svmip in svmips:
        sshCopyid(svmip)
    hostlist =  output[0].replace(" ", ",")
    while 1:
        cvm = (random.shuffle(hostlist)).pop()
        print "Run test on the CVM -> ",+cvm
        runS(ssh+acli,cvm,container,imgp)

def runS(ssh,cvm,container,imgp):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    vcpus = 4
    bdisksize = '8G'
    edisksize = '400G'
    vmcount = 15
    imgp = "oltp,fioS,strS" 
    container = "long_test_cont_1,long_test_cont_2,long_test_cont_3"

    t = threading.Thread(target=vmCreate, args=(ssh,cvm,vmcount,bdisksize,vcpus,hostlist,container,edisksize,imgp,userid))
    threads.append(t)
    t = threading.Thread(target=vmDelDisk, args=(ssh,"clone",))
    threads.append(t)
    t = threading.Thread(target=vmAddDisk, args=(ssh,"clone",container,))
    threads.append(t)
    t = threading.Thread(target=vmMigrate, args=(ssh,"clone",))
    threads.append(t)
    threads.append(t)
    t = threading.Thread(target=delVmbyPattern, args=(ssh,"clone",))
    threads.append(t)


    for x in threads: 
        x.start()
        time.sleep(5)

    for x in threads: 
        x.join()

     

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



if __name__ == "__main__":
    main(sys.argv[1:])


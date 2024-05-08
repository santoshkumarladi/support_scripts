#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import itertools


def delVmbyPattern(ssh,cvm,vname):
    run = ssh +" vm.list | grep \""+vname+"\""
    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    print run
    output = (os.popen(run).read()).split('\n')
    print output
    for i in range(1,len(output)-1):
        #VM name  VM UUID
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.delete "+uuid
        print cmd
        os.system(cmd)
        try:
            cmd = ncli +"pd clear-schedules name=testPD_"+vm
            print cmd
            os.system(cmd)
            cmd = ncli + " pd rm-snap name=testPD_"+vm+" clear-all=true "
            print cmd
            os.system(cmd)
            cmd = ncli +" pd unprotect name=testPD_"+vm+" vm-names="+vm
            print cmd
            os.system(cmd)
            cmd = ncli + " pd remove name=testPD_"+vm
            print cmd
            os.system(cmd)
        except Exception as e:
            print op

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

            
def vmCreateDelete(ssh,count,wait,vm):
    vmlist = []
    vmclone = []
    for i in range(count):
        vmname = vm+"_"+str(random.randint(100,128908))
        cmd = ssh+" vm.create "+vmname
        print cmd
        os.system(cmd)
        #time.sleep(wait)
        vmlist.append(vmname)
       
    createNestedClone(ssh,vmname,count,vmclone)

    for clvm in vmclone:
        vmcloneOpt(ssh,clvm)

    for vmname  in (vmlist):
        cmd = ssh+" vm.delete "+vmname
        print cmd
        os.system(cmd)
        #time.sleep(wait)

def vmMigrate(ssh,vname,count,hostlist,wait):
    run = ssh +" vm.list power_state=on | grep \""+vname+"\""
    print run 
    output = (os.popen(run).read()).split('\n')
    print "Loop count -> "+str(count)+ " and wait "+str(wait)
    j=0

    for i in range(1,len(output)-1):
        #vm.migrate long_run_vm_11 live=true
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.affinity_set "+vm+" host_list="+hostlist
        print cmd
        os.system(cmd)
        cmd = ssh+" vm.migrate "+uuid+" live=true"
        print cmd 
        os.system(cmd)
        if j < count :
            j=j+1
        else :
            j=0
            time.sleep(wait)

def vmAddDisk(ssh,vname,vdsize,container):
    run = ssh +" vm.list"+" | grep \""+vname+"\""
    print run 
    k=0
    output = (os.popen(run).read()).split('\n')
    for i in range(1,len(output)-1):
        #vm.disk_create long_run_vm_2 container=long_test_cont_1 create_size=400G
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.disk_create "+uuid+" container="+container[k]+ " create_size="+vdsize
        print cmd 
        os.system(cmd)
        k = k+1 if k < len(container)-1 else 0

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
        cmd = ssh+" vm.disk_list "+uuid
        print cmd 
        ou = (os.popen(cmd).read()).split('\n')
        if (len(ou)-1) > 2:
            for i in range(3,len(ou)-1):
                (bus,did) = ou[i].split()
                cmd = ssh+" vm.disk_delete "+uuid+" disk_addr=scsi."+did
                print cmd 
                os.system(cmd)

def pdCreate(run,vm,nosnap,remote):
    cmd = run +" pd create name=testPD_"+vm
    print cmd
    os.system(cmd)
    cmd = run +" pd protect name=testPD_"+vm+" vm-names="+vm+" cg-name=testCG"+vm
    print cmd
    os.system(cmd)

    nosnap=8
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

def vmCreate(ssh,cvm,vmcount,patern,bdisksize,vcpus,disks,hostlist,containername,edisksize,imgp,userid):

    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "
    run = ssh+acli
    remote = ""
    nosnap=8
    j=k=0

    for i in range (vmcount):
        if imgp[j] == 'oltpS':
            memory='4G'
            vdisks=6
            vdisk_size = '32G'
            vcpu=2
            cores=1
        elif imgp[j] == 'fioS':
            memory='20G'
            vdisks=8
            vdisk_size = '20G'
            vcpu=2
            cores=2
        elif imgp[j] == 'vdbS':
            memory='4G'
            vdisks=4
            vdisk_size = '300G'
            vcpu=2
            cores=1
        elif imgp[j] == 'strS':
            memory='15G'
            vdisks=16
            vdisk_size = '52G'
            vcpu=4
            cores=1
        elif imgp[j] == 'winS':
            memory='40G'
            vdisks=8
            vdisk_size = '52G'
            vcpu=2
            cores=1
        elif imgp[j] == 'tiltS':
            memory='20G'
            vdisks=8
            vdisk_size = '50G'
            vcpu=2
            cores=1
        if disks:
            vdisks = disks 
        #vm.create long_run_vm_2 memory=8G num_vcpus=4
        vmname = patern+imgp[j]+"_vm_"+str(random.randint(100,128908))
        cmd = run+ " vm.create "+vmname+" memory="+memory+" num_vcpus="+str(vcpu)+" num_cores_per_vcpu="+str(cores)
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
        k = k+1 if k < len(containername)-1 else 0
        for i in range(vdisks): 
            #vm.disk_create long_run_vm_2 container=long_test_cont_1 create_size=400G
            cmd = run+" vm.disk_create "+vmname+" container="+containername[k]+" create_size="+vdisk_size
            print cmd
            os.system(cmd)

        pdCreate(ssh+ncli,vmname,nosnap,remote)
        if j < len(imgp)-1:
            j=j+1
        else :
            j=0
        

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

def createSnapshot (ssh,vm,count,wait):
    print 'Create snaphot  '
    for i in range(count):
        snapname = "testSnap"+str(random.randint(100,128908))
        cmd = " vm.snapshot_create "+vm+" snapshot_name_list="+snapname
        run = ssh+cmd
        print run
        os.system(run)
        time.sleep(wait)

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

def main(argv):
    cmd = ''
    tasks = ''
    paterns = 'gold'
    wait = 1200
    runs = 1
    nofv = 10
    vdisks = 0
    userid = 'nutanix'
    imgp = "oltpS,tiltS,fioS,strS,winS,vdbS"
    container = "long_test_cont_1,long_test_cont_2,long_test_cont_3,long_test_cont_4"
    #imgp = '/long_test_cont_1/CentOS7.2.img'
    #container = 'long_test_cont_1'

    try:
        opts, args = getopt.getopt(argv,"hc:r:m:t:p:l:w:v:n:",["cvm=","container=","imgp=","tasks=","patern=","nofv=","vdisks","wait=","runs="])
    except getopt.GetoptError:
        print 'vmOptSmall.py -c <cvm> -r <container> -m <imgp> -t <task vmCreate,vmDelDisk,vmAddDisk,vmMigrate,delVmbyPattern,vmCreateDelete > -l <no of vms> -v <vdisks> -n <no of runs> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'vmOptSmall.py -c <cvm> -r <container> -m <imgp> -t <task vmCreate,vmDelDisk,vmAddDisk,vmMigrate,delVmbyPattern,vmCreateDelete > -l <no of vms> -v <vdisks> -n <no of runs> -w <wait>'
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-r", "--container"):
            container = arg
        elif opt in ("-m", "--imgp"):
            imgp = arg
        elif opt in ("-t", "--task"):
            tasks = arg
        elif opt in ("-p", "--patern"):
            paterns = arg
        elif opt in ("-l", "--nofv"):
            nofv = int(arg)
        elif opt in ("-v", "--vdisk"):
            vdisks = int(arg)
        elif opt in ("-w", "--wait"):
            wait = int(arg)
        elif opt in ("-n", "--runs"):
            runs = int(arg)

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    for  svmip in svmips:
        sshCopyid(svmip)
    lst = output[0].split()


    run = ssh+" /usr/local/nutanix/cluster/bin/hostips"
    output = (os.popen(run).read()).split('\n')
    hostplist =  output[0].replace(" ", ",")
    print hostplist

    tasks = tasks.split(',')
    paterns = paterns.split(',')
    imgp = imgp.split(',')
    container = container.split(',')

    for i in range(runs):
        random.shuffle(lst)
        cvm = lst[len(lst)-1]
        print "Run test on the CVM -> "+cvm+" patern "
        runS(ssh+acli,cvm,container,imgp,hostplist,tasks,nofv,vdisks,paterns,wait)
        if i<1:
            time.sleep(wait)

def runS(ssh,cvm,container,imgp,hostlist,tasks,vmcount,vdisks,paterns,wait):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    vcpus = 4
    bdisksize = '8G'
    edisksize = '400G'
    #vmcount = 40
    count = 2
    for (task,patern) in itertools.izip(tasks,paterns):
        if task == 'vmCreate':
            vmCreate(ssh,cvm,vmcount,patern,bdisksize,vcpus,vdisks,hostlist,container,edisksize,imgp,userid)
        elif task == 'vmAddDisk':
            vmAddDisk(ssh,patern,edisksize,container)
        elif task == 'vmMigrate':
            vmMigrate(ssh,patern,count,hostlist,wait)
        elif task == 'delVmbyPattern':
            delVmbyPattern(ssh,cvm,patern)
        elif task == 'vmCreateDelete':
            vmCreateDelete(ssh,count,wait,patern)
        elif task == 'vmDelDisk':
            vmDelDisk(ssh,patern)
    time.sleep(wait)


if __name__ == "__main__":
    main(sys.argv[1:])


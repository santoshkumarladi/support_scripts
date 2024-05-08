#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import itertools
import threading

def setUpLVM(ssh,cvm,vmname):
    ip=''
    devList = []
    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    run = ncli+" vm list name="+vmname+" | grep \"VM IP Addresses\""
    print run
    match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
    if match is not None:
        ip = match.group()
        print vmname+"  "+ip
    else :
        cmd = ssh+" vm.power_cycle "+vmname
        print cmd
        os.system(cmd)
        time.sleep(120)
        run = ncli+" vm list name="+vmname+" | grep \"VM IP Addresses\""
        print run
        match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
        if match is not None:
            ip = match.group()
            print vmname+"  "+ip
    if ip:
        sshCopyid(ip,"root")
        cmd = "scp -r /home/santoshkumar.ladi/scripts/setup/setupLargeClient.sh root@"+str(ip)+":/home/nutanix/"
        print cmd
        os.system(cmd)
        cmd = "scp -r /home/santoshkumar.ladi/scripts/setup/rc.local root@"+str(ip)+":/etc/rc.d/rc.local"
        print cmd
        os.system(cmd)
        cmd = "ssh "+ip+" -l root \" sudo chmod +x /etc/rc.d/rc.local\""
        print cmd
        os.system(cmd)
    if 0:
        cmd = "ssh "+ip+" -l nutanix \" sudo sed -i '\$ a sleep 60\\\\n/usr/bin/sh /home/nutanix/setupLargeClient.sh\\\\nexit 0' /etc/rc.local \""
        print cmd
        os.system(cmd)
        cmd = "ssh "+ip+" -l nutanix \" sudo sed -i '\$ a sleep 60\\\\n/usr/bin/sh /home/nutanix/setupLargeClient.sh\\\\nexit 0' /etc/rc.d/rc.local \""
        print cmd
        os.system(cmd)
        cmd = "ssh "+ip+" -l nutanix \" sudo cat /etc/rc.d/rc.local\""
        print cmd
        os.system(cmd)
        sshCopyid(ip)
        cmd = "scp -r /home/santoshkumar.ladi/scripts/setup/setupLargeClient.sh nutanix@"+str(ip)+":/home/nutanix/"
        print cmd
        os.system(cmd)
        cmd = "ssh "+ip+" -l nutanix \"/usr/bin/lsblk -S -f -s | grep -v rom\""
        output = (os.popen(cmd).read()).split('\n')
        for i in range(1,len(output)-1):
            if 'ext4' not in output[i] :
                line = output[i].split()
                devList.append("/dev/"+line[0])
                try:
                    #sudo mkfs.ext4 -T largefile4 /dev/sdb1 -b 4096
                    cmd = "ssh "+ip+" -l nutanix \"sudo mkfs.ext4 -F /dev/"+str(line[0])+";sudo mkdir /my_vol_"+str(vmname)+";sudo mount -t ext4 /dev/"+str(line[0])+" /my_vol_"+str(vmname)+" \""
                    print cmd
                    if os.system(cmd) != 0 :
                        raise Exception('Cmd failed!')
                    # uuid=$(blkid -s UUID -o value /dev/$b)
                    # echo "UUID=$uuid  /root/abcd  ext4 defaults 0 0" >> /etc/fstab
                    cmd = "ssh "+ip+" -l nutanix \" sudo sed -i -e \'$i /dev/"+str(line[0])+" /my_vol_"+str(vmname)+" ext4   defaults    0   0 \\\n\' /etc/fstab \""
                    #cmd = "ssh "+ip+" -l nutanix \"sudo echo \"/dev/"+str(line[0])+" /my_vol_"+str(vmname)+" ext4   defaults    0   0 \""
                    print cmd
                    if os.system(cmd) != 0 :
                        raise Exception('Cmd failed!')
                    #sudo sed -i -e '$i \nohup sh /home/nutanix/setupLargeClient.sh &\n' /etc/rc.local
                    cmd = "ssh "+ip+" -l nutanix \" sudo sed -i -e \'$i \\\nohup sh /home/nutanix/setupLargeClient.sh \\&\\\n\' /etc/rc.local \""
                    print cmd
                    os.system(cmd)
                except :
                    print "Config part failed check the init and start again "
                    sys.exit()


def vmCreateLarge(run,cvm,vmcount,patern,bdisksize,vcpus,disks,hostlist,containername,edisksize,imgp,userid,remote):

    ncli = "ssh "+cvm+" -l "+userid+" /home/nutanix/prism/cli/ncli "
    #remote = ""
    vmList = []
    nosnap=8
    j=k=0

    for i in range (vmcount):
        if imgp[j] == 'oltpS':
            memory='4G'
            vdisks=6
            vdisk_size = '32G'
            vcpu=4
            cores=1
        elif imgp[j] == 'fioS':
            memory='20G'
            vdisks=8
            vdisk_size = '20G'
            vcpu=4
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
            vcpu=8
            cores=1
        elif imgp[j] == 'winS':
            memory='40G'
            vdisks=8
            vdisk_size = '52G'
            vcpu=4
            cores=2
        elif imgp[j] == 'tiltS':
            memory='20G'
            vdisks=8
            vdisk_size = '50G'
            vcpu=4
            cores=1
        elif imgp[j] == 'largS':
            memory='4G'
            vdisks=1
            vdisk_size = edisksize
            vcpu=4
            cores=1
        elif imgp[j] == 'vgcS':
            memory='8G'
            vdisks=1
            vdisk_size = edisksize
            vcpu=4
            cores=1

        if disks:
            vdisks = disks 
        #vm.create long_run_vm_2 memory=8G num_vcpus=4
        vmname = patern+imgp[j]+"_largevm_"+str(random.randint(100,128908))
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

        pdCreate(ncli,vmname,nosnap,remote)
        cmd = run+ " vm.on "+vmname
        print cmd
        os.system(cmd)
        vmList.append(vmname)
        if j < len(imgp)-1:
            j=j+1
        else :
            j=0

    time.sleep(30)
    for vm in (vmList):
        setUpLVM(run,cvm,vm)
 
    cmd = run+" vm.power_cycle "+patern+imgp[j]+"_largevm_"+"*"
    print cmd
    os.system(cmd)

def delVmbyPattern(ssh,cvm,vname):
    run = ssh +" vm.list | grep \""+vname+"\""
    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    print run
    output = (os.popen(run).read()).split('\n')
    print output
    for i in range(0,len(output)-1):
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
    print "_______________________________________> "+remote
    nosnap=8
    if remote:
        cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" remote-retention="+remote+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
        print cmd
    else:
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

def pdCreates(cvm,vmname,remote):
    ncli = " /home/nutanix/prism/cli/ncli "
    ssh = "ssh "+cvm+" -l nutanix"
    acli = ssh+" /usr/local/nutanix/bin/acli -y"
    cmd = acli +" vm.list | grep \""+vmname+"\""
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    print output
    for i in range(1,len(output)-1):
        #VM name  VM UUID
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        (vm,uuid) = output[i].split()
        run = ssh+ncli
        cmd = run +" pd create name=testPD_"+vm
        print cmd
        os.system(cmd)
        cmd = run +" pd protect name=testPD_"+vm+" vm-names="+vm+" cg-name=testCG"+vm
        print cmd
        os.system(cmd)
        print "_______________________________________> "+remote
        nosnap=8
        cmd = run +"\" pd clear-schedules name=testPD_"+vm
        print cmd
        os.system(cmd)
        if remote:
            cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" remote-retention="+remote+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
            print cmd
        else:
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

def vmCreate(run,cvm,vmcount,patern,bdisksize,vcpus,disks,hostlist,containername,edisksize,imgp,userid,remote):

    ncli = "ssh "+cvm+" -l "+userid+" /home/nutanix/prism/cli/ncli "
    #remote = ""
    nosnap=8
    j=k=0

    for i in range (vmcount):
        if imgp[j] == 'oltpS':
            memory='4G'
            vdisks=6
            vdisk_size = '32G'
            vcpu=4
            cores=1
        elif imgp[j] == 'fioS':
            memory='20G'
            vdisks=8
            vdisk_size = '20G'
            vcpu=4
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
            vcpu=8
            cores=1
        elif imgp[j] == 'winS':
            memory='40G'
            vdisks=8
            vdisk_size = '52G'
            vcpu=4
            cores=2
        elif imgp[j] == 'tiltS':
            memory='20G'
            vdisks=8
            vdisk_size = '50G'
            vcpu=4
            cores=1
        elif imgp[j] == 'largS':
            memory='4G'
            vdisks=1
            vdisk_size = edisksize
            vcpu=4
            cores=1
        else :
            memory='8G'
            vdisks=1
            vdisk_size = edisksize
            vcpu=4
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
        if imgp[j] == 'largS':
            cmd = run+" vm.disk_create "+vmname+" clone_from_image=vdbS"
        else : 
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

        pdCreate(ncli,vmname,nosnap,remote)
        if j < len(imgp)-1:
            j=j+1
        else :
            j=0

def createNestedCl(ssh,clone_from_vm,count):
    for i in range(count):
        clone_name = clone_from_vm+"random"+str(random.randint(100,128908))
        cmd = ssh+ " vm.clone " +clone_name+" clone_from_vm=" + clone_from_vm+" memory=4G num_cores_per_vcpu=1 num_vcpus=2"
        print cmd
        op = os.popen(cmd).read()
        #complete
        #match = re.match(r'(.*):\s+complete(.*)', op)
        time.sleep(60)
        if re.search(r'complete',op):
            cmd = ssh+ " vm.on " +clone_name
            print cmd
            os.system(cmd)
            clone_from_vm = clone_name
        else :
            break        

def vmClone(cvm,count,pat,wait):
    ssh = "ssh "+cvm+" -l nutanix"
    acli = " /usr/local/nutanix/bin/acli -y"
    delVmbyPattern(ssh + acli,cvm,"random")
    run = ssh +acli+" vm.list | grep \""+pat+"\" | grep -v \"VM name\" "
    output = (os.popen(run).read()).split('\n')
    random.shuffle(output)
    try:
        for i in range(count):
            if output[i]:
                (vm,uuid) = output[i].split()
                createNestedCl(ssh+acli,vm,count)
        pdCreates(cvm,patern,"")
    except Exception as e:
        print "Clone create failed "
    time.sleep(wait)


def sshCopyid(ip,userid):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    rsa_key = '\(yes\/no\)\?'
    prompt = "assword:"
    non_rsa='you wanted were added.'

    cmd = "ssh-keygen -R "+str(ip)
    os.system(cmd)
    cmd = " /usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no "+userid+"@"+str(ip)
    print cmd
    child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no %s@%s'%(userid,ip))
    #r=child.expect ('you wanted were added.')
    r= child.expect([non_rsa,rsa_key,prompt,pexpect.EOF],timeout=30)
    print "Outp"+str(r)
    if r==0:
        print "Outp 0"
        child.interact()
        child.close()
    elif r==1:
        print "Outp 1"
        child.sendline('yes')
        child.expect(prompt)
        child.sendline(passwd)
    elif r==2:
        print "Outp 2"
        child.sendline(passwd)
    elif r==3:
        print "Outp 3"
        child.sendline(passwd)
        child.interact()
        child.close()
    else :
        print "Outp 4"
        child.expect(prompt)
        child.sendline(passwd)

    child.interact()
    child.close()


    """
    cmd = "ssh-keygen -R "+str(ip)
    os.system(cmd)
    cmd = " /usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@"+str(ip)
    print cmd
    child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@%s'%(ip))
    r=child.expect ('you wanted were added.')
    print "Outp"+str(r)
    #if r==0:
    #    child.sendline (passwd)
    child.interact()
    child.close()
    """
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

def get_svmips(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    print "Op ---> "+op
    if op :
        output = op.split('\n')
        for i in range(1,len(output)):
            if output[i].split()[4] != 'False' and output[i].split()[6] != 'False':
                svmips.append(output[i].split()[-1])

        return svmips

def vmCreateSmall(run,cvm,vmcount,patern,hostlist,containername,userid,remote):

    ncli = "ssh "+cvm+" -l "+userid+" /home/nutanix/prism/cli/ncli "
    #remote = ""
    vmList = []
    nosnap=8
    k=0
    imgp = 'fioS'
    memory='2G'
    vdisks=1
    vdisk_size = '10G'
    vcpu=2
    cores=1

    for i in range (vmcount):
        #vm.create long_run_vm_2 memory=8G num_vcpus=4
        vmname = patern+imgp+"_smallvm_"+str(random.randint(100,128908))
        cmd = run+ " vm.create "+vmname+" memory="+memory+" num_vcpus="+str(vcpu)+" num_cores_per_vcpu="+str(cores)
        print cmd
        os.system(cmd)
        #vm.disk_create testVM clone_from_adsf_file=/nutest_ctr_0/nutest/goldimages/ahv/Centos_QOS-1.0/Centos72_QOS.img
        #cmd = run+" vm.disk_create "+vmname+" clone_from_adsf_file="+imgp
        cmd = run+" vm.disk_create "+vmname+" clone_from_image="+imgp
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

        cmd = run+ " vm.on "+vmname
        print cmd
        os.system(cmd)
        vmList.append(vmname)

    pdCreateMul(ncli,vmList,nosnap,"smallvm",remote)


def pdCreateMul(run,vmL,nosnap,pat,remote):
    cmd = run +" pd create name=testPD_"+pat
    print cmd
    os.system(cmd)

    for vm in vmL:
        cmd = run +" pd protect name=testPD_"+pat+" vm-names="+vm
        print cmd
        os.system(cmd)

    print "_______________________________________> "+remote
    nosnap=8
    if remote:
        cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" remote-retention="+remote+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
        print cmd
    else:
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


def main(argv):
    cmd = ''
    tasks = ''
    remote = ''
    paterns = 'gold'
    wait = 1200
    runs = 1
    nofv = 10
    vdisks = 0
    vdsize = "1000G"
    userid = 'nutanix'
    imgp = "oltpS,tiltS,fioS,strS,winS,vdbS,xray"
    container = "long_test_cont_1,long_test_cont_2,long_test_cont_3,long_test_cont_4"
    #imgp = '/long_test_cont_1/CentOS7.2.img'
    #container = 'long_test_cont_1'

    try:
        opts, args = getopt.getopt(argv,"hc:d:r:m:t:p:l:w:v:s:n:",["cvm=","remote=","container=","imgp=","tasks=","patern=","nofv=","vdisks","wait=","runs=","dsize="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -d <dest/remote server> -r <container> -m <imgp> -t <task vmCreate,vmDelDisk,vmAddDisk,vmMigrate,vmClone,delVmbyPattern,vmCreateDelete,pdCreates > -l <no of vms> -v <vdisks> -s <vdsize> -n <no of runs> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -d <dest/remote server> -r <container> -m <imgp> -t <task vmCreate,vmDelDisk,vmAddDisk,vmMigrate,delVmbyPattern,vmCreateDelete,pdCreates > -l <no of vms> -v <vdisks> -s <vdsize> -n <no of runs> -w <wait>'
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
        elif opt in ("-d", "--remote"):
            remote  = arg
        elif opt in ("-l", "--nofv"):
            nofv = int(arg)
        elif opt in ("-v", "--vdisk"):
            vdisks = int(arg)
        elif opt in ("-s", "--dsize"):
            vdsize = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)
        elif opt in ("-n", "--runs"):
            runs = int(arg)

    sshCopyid(cvm,"nutanix")
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    cvmips=get_svmips(cvm)
    for  cvmip in cvmips:
        sshCopyid(cvmip,"nutanix")

    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
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
        print "Run test on the CVM -> "+cvm+" patern "+remote
        runS(ssh+acli,cvm,container,imgp,hostplist,tasks,nofv,vdisks,paterns,vdsize,wait,remote)
        if i<1:
            time.sleep(wait)

def runS(ssh,cvm,container,imgp,hostlist,tasks,vmcount,vdisks,paterns,edisksize,wait,remote):
    threads = []
    sshCopyid(cvm,"nutanix")
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    vcpus = 4
    bdisksize = '8G'
    #vmcount = 40
    count = 12
    for (task,patern) in itertools.izip(tasks,paterns):
        if task == 'vmCreate':
            t = threading.Thread(target=vmCreate, args=(ssh,cvm,vmcount,patern,bdisksize,vcpus,vdisks,hostlist,container,edisksize,imgp,userid,remote))
            threads.append(t)
            t.start()
            time.sleep(240)
        elif task == 'vmCreateLarge':
            img=["vgcS"]
            edisksz="25000g"
            vdisk=1
            t = threading.Thread(target=vmCreateLarge, args=(ssh,cvm,vmcount,patern,bdisksize,vcpus,vdisk,hostlist,container,edisksz,img,userid,remote))
            threads.append(t)
            t.start()
            time.sleep(240)
        elif task == 'vmCreateSmall':
            vmcnt=100
            t = threading.Thread(target=vmCreateSmall, args=(ssh,cvm,vmcnt,patern,hostlist,container,userid,remote))
            threads.append(t)
            t.start()
            time.sleep(240)
        elif task == 'vmAddDisk':
            t = threading.Thread(target=vmAddDisk, args=(ssh,patern,edisksize,container))
            threads.append(t)
            t.start()
            time.sleep(240)
        elif task == 'vmMigrate':
            t = threading.Thread(target=vmMigrate, args=(ssh,patern,count,hostlist,wait))
            threads.append(t)
            t.start()
            time.sleep(240)
        elif task == 'vmClone':
            t = threading.Thread(target=vmClone, args=(cvm,count,patern,wait))
            threads.append(t)
            t.start()
            time.sleep(240)
        elif task == 'delVmbyPattern':
            t = threading.Thread(target=delVmbyPattern, args=(ssh,cvm,patern))
            threads.append(t)
            t.start()
            time.sleep(240)
        elif task == 'vmCreateDelete':
            t = threading.Thread(target=vmCreateDelete, args=(ssh,count,wait,patern))
            threads.append(t)
            t.start()
            time.sleep(240)
        elif task == 'vmDelDisk':
            t = threading.Thread(target=vmDelDisk, args=(ssh,patern))
            threads.append(t)
            t.start()
            time.sleep(240)
        elif task == 'pdCreates':
            t = threading.Thread(target=pdCreates, args=(cvm,patern,remote))
            threads.append(t)
            t.start()
            time.sleep(240)
    for x in threads:
        x.join()
        time.sleep(wait)


if __name__ == "__main__":
    main(sys.argv[1:])


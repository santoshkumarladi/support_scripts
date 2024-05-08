#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import itertools


def get_clusterDetails(cvm):
    List = {}

    ncli = " /home/nutanix/prism/cli/ncli "
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh +ncli+"cluster info "
    print run
    ctr = os.popen(run).read()
    if ctr:
        ctr = ctr.split('\n')
        for ctrN in ctr:
            if ctrN:
                (key,val)=ctrN.split(" : ")
                key=key.strip()
                List[key]=val
                #print "key "+str(key)+" val "+str(val)
    return List

def setupRemote(cvml,reten):
    cls = {}
    clist = {}
 
    for cvm in cvml :
        sshCopyid(cvm,"nutanix")
        cls = get_clusterDetails(cvm)
        clsname = cls["Cluster Name"] 
        clist[cvm]=clsname

    for cvm in cvml:
        remote = []
        for dcvm in cvml:
            if dcvm != cvm:
                print cvm
                ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
                run = ncli+" remote-site add addresses="+str(dcvm)+" name="+clist[dcvm]
                print run
                os.system(run)
                remote.append(clist[dcvm]+":"+str(reten))
                rem =','.join([i for i in remote  if i])
        print rem
        pdCreates(cvm,"test",rem)


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




def vmCreateSmall(run,cvm,vmcount,patern,hostlist,containername,userid,vlan,remote,pd):

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
        cmd =run+ " vm.nic_create "+vmname+" network="+vlan
        print cmd
        os.system(cmd)
        #vm.affinity_set long_run_vm_2 host_list=10.46.32.121,10.46.32.122
        #cmd = run+" vm.affinity_set "+vmname+" host_list="+hostlist
        #print cmd
        #os.system(cmd)
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
    if pd:
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
        cmd = run +"\" pd add-hourly-schedule name=testPD_"+pat+" local-retention="+str(nosnap)+" remote-retention="+remote+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
        print cmd
    else:
        cmd = run +"\" pd add-hourly-schedule name=testPD_"+pat+" local-retention="+str(nosnap)+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
        print cmd

    os.system(cmd)
    nosnap=10
    cmd = run +"\" pd add-hourly-schedule name=testPD_"+pat+" local-retention="+str(nosnap)+" every-nth-hour=6 start-time=\\\"02/14/2018 18:30:00 UTC\\\"\""
    print cmd
    os.system(cmd)
    nosnap=5
    cmd = run +"\" pd add-daily-schedule name=testPD_"+pat+" local-retention="+str(nosnap)+" start-time=\\\"02/14/2018 09:30:00 UTC\\\"\""
    print cmd
    os.system(cmd)

#vmCreateLarge(ssh,cvm,vmcount,patern,bdisksize,vcpus,vdisk,hostlist,container,edisksz,img,userid,vlan,remote)
def vmCreateLarge(run,cvm,vmcount,patern,bdisksize,vcpus,disks,hostlist,containername,edisksize,imgp,userid,vlan,remote,pd):

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
        cmd =run+ " vm.nic_create "+vmname+" network="+vlan
        print cmd
        os.system(cmd)
        #vm.affinity_set long_run_vm_2 host_list=10.46.32.121,10.46.32.122
        #cmd = run+" vm.affinity_set "+vmname+" host_list="+hostlist
        #print cmd
        #os.system(cmd)
        cmd = run+" vm.on "+vmname
        print cmd
        os.system(cmd)

        k = k+1 if k < len(containername)-1 else 0
        for i in range(vdisks): 
            #vm.disk_create long_run_vm_2 container=long_test_cont_1 create_size=400G
            cmd = run+" vm.disk_create "+vmname+" container="+containername[k]+" create_size="+vdisk_size
            print cmd
            os.system(cmd)
        if pd:
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

def delPdbyPattern(ssh,cvm,vname):

    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    cmd = ncli +"pd list | grep \"Protection Domain\" | grep \""+vname+"\""
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    for i in range(0,len(output)-1):
        (tmp,pd) = output[i].split(":")
        cmd = ncli+" pd clear-schedules name="+pd.strip()
        print cmd
        os.system(cmd)
        cmd = ncli + " pd rm-snap name="+pd.strip()+" clear-all=true "
        print cmd
        os.system(cmd)
        cmd = ncli + " pd list name="+pd.strip()+" | grep \"VM Name\" "
        print cmd
        out = (os.popen(cmd).read()).split('\n')
        for i in range(0,len(out)-1):
            vmname = out[i].split(":")[1]
            cmd = ncli +" pd unprotect name="+pd.strip()+" vm-names="+vmname.strip() 
            print cmd
            os.system(cmd)
        cmd = ncli + " pd remove name="+pd.strip()
        print cmd
        os.system(cmd)

def delVm(ssh,cvm,vname):

    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    #VM name  VM UUID
    #vm1      f347f020-5b42-481f-a2a4-74aad770a333
    cmd = ssh+" vm.delete "+vname
    print cmd
    os.system(cmd)
    try:
        pd="testPD_"+vname
        cmd = ncli +"pd clear-schedules name="+pd
        print cmd
        os.system(cmd)
        cmd = ncli + " pd rm-snap name=testPD_"+vmname+" clear-all=true "
        print cmd
        os.system(cmd)
        if vname == 'small':
            ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
            run = ssh +" vm.list | grep \""+vname+"\" "
            print run
            output = (os.popen(run).read()).split('\n')
            for i in range(0,len(output)-1):
                for vsmall in output:
                    (vm,uuid) = output[i].split()
                    cmd = ncli +" pd unprotect name=testPD_"+vmname+" vm-names="+vm
                    print cmd
                    os.system(cmd)
        else :
            cmd = ncli +" pd unprotect name=testPD_"+vmname+" vm-names="+vmname
            print cmd
            os.system(cmd)
                
        cmd = ncli + " pd remove name=testPD_"+vmname
        print cmd
        os.system(cmd)
    except Exception as e:
        print "Failed "

def delVmbyPattern(ssh,cvm,vname):
    run = ssh +" vm.list | grep \""+vname+"\" "

    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    cmd = ncli +"pd list | grep \"Protection Domain\" | grep \""+vname+"\""
    print cmd
    out = (os.popen(cmd).read())

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
            pd="testPD_"+vm
            if pd in out: 
                cmd = ncli +"pd clear-schedules name="+pd
                print cmd
                os.system(cmd)
                cmd = ncli + " pd rm-snap name=testPD_"+vm+" clear-all=true "
                print cmd
                os.system(cmd)
                if vname == 'small':
                    for vsmall in output:
                        (vm,uuid) = output[i].split()
                        cmd = ncli +" pd unprotect name=testPD_"+vm+" vm-names="+vm
                        print cmd
                        os.system(cmd)
                else :
                    cmd = ncli +" pd unprotect name=testPD_"+vm+" vm-names="+vm
                    print cmd
                    os.system(cmd)
                
                cmd = ncli + " pd remove name=testPD_"+vm
                print cmd
                os.system(cmd)
        except Exception as e:
            print op

def delVgbyPattern(ssh,cvm,vgame):
    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    cmd = ssh+" vg.list | grep "+vgame
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    for i in range(0,len(output)-1):
        (vg,uuid) = output[i].split()
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

            
def vmCreateDelete(ssh,count,wait,vm,vdsize,container):
    vmlist = []
    vmclone = []
    for i in range(count):
        vmname = vm+"_"+str(random.randint(100,128908))
        cmd = ssh+" vm.create "+vmname
        print cmd
        os.system(cmd)
        vmAddDisk(ssh,vmname,vdsize,container)
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
        cmd = run +"\" pd clear-schedules name=testPD_"+vm.strip()+"\""
        print cmd
        os.system(cmd)
        if remote:
            cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" remote-retention="+remote+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
            print cmd
            os.system(cmd)
            remote = ','.join([i.split(':')[0] for i in remote.split(',')  if i])
            cmd = run +"\" pd create-one-time-snapshot remote-sites="+remote+" name=testPD_"+vm+" retention-time="+str(random.randint(100,128)) +"\""
            print cmd
            os.system(cmd)
        else:
            cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
            print cmd
            os.system(cmd)

        os.system(cmd)
        nosnap=10
        cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" every-nth-hour=6 start-time=\\\"02/14/2018 18:30:00 UTC\\\"\""
        print cmd
        os.system(cmd)
        nosnap=5
        cmd = run +"\" pd add-daily-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" start-time=\\\"02/14/2018 09:30:00 UTC\\\"\""
        print cmd
        os.system(cmd)


def createCl(ssh,clone_from_vm,clone_name,count):
    for i in range(count):
        cmd = ssh+ " vm.clone " +clone_name+" clone_from_vm=" + clone_from_vm+" memory=4G num_cores_per_vcpu=1 num_vcpus=2"
        print cmd
        op = os.popen(cmd).read()
        if re.search(r'complete',op):
            cmd = ssh+ " vm.on " +clone_name
            print cmd
            os.system(cmd)
            clone_from_vm = clone_name
            time.sleep(60)
        else :
            break


def vmSnC(run,cvm,vmcount,bdisksize,vcpus,disks,hostlist,containername,edisksize,randomvd,imgp,userid,remote,vlan,wait,pd):
    clone_from_vm=""
    parent=""
    
    parent = "parentVm"+str(random.randint(100,128908))
    print "Create the Parent VM --> "+str(parent)
    vmCreate(run,cvm,1,parent,bdisksize,vcpus,disks,hostlist,containername,edisksize,randomvd,imgp,userid,vlan,remote,pd)
    time.sleep(wait)
    print "Sleep  for  --> "+str(wait)
    cmd = run +" vm.list | grep \""+parent+"\" "
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    for j in range(0,len(output)-1):
        (parent,uuid) = output[j].split()
        clone_from_vm  = parent
        for i in range (vmcount):
            child="childVm" +str(random.randint(100,128908))
            print "Create the Child VM --> "+str(child)
            createCl(run,clone_from_vm,child,1)
            print "Create snapshot policy->"+str(child) +"  Remote  -->"+str(remote)
            if pd:
                pdCreates(cvm,child,remote)
            print "Delete vm -------->"+str(clone_from_vm)
            delVm(run,cvm,clone_from_vm)
            clone_from_vm = child
            print "The Child is now parent VM --> "+str(clone_from_vm)


def vmCreate(run,cvm,vmcount,patern,bdisksize,vcpus,disks,hostlist,containername,edisksize,randomvd,imgp,userid,vlan,remote,pd):

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
        elif imgp[j] == 'ioInt':
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
        op = os.popen(cmd).read()
        time.sleep(60)
        print op
        if re.search(r'complete',op):
            #vm.disk_create testVM clone_from_adsf_file=/nutest_ctr_0/nutest/goldimages/ahv/Centos_QOS-1.0/Centos72_QOS.img
            #cmd = run+" vm.disk_create "+vmname+" clone_from_adsf_file="+imgp
            if imgp[j] == 'largS':
                cmd = run+" vm.disk_create "+vmname+" clone_from_image=vdbS"
                if edisksize:
                    vdisk_size = edisksize
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
                if randomvd:
                    vdisk_size = str(random.randint(1,500))+"G"
                #vm.disk_create long_run_vm_2 container=long_test_cont_1 create_size=400G
                cmd = run+" vm.disk_create "+vmname+" container="+containername[k]+" create_size="+vdisk_size
                print cmd
                os.system(cmd)
            if pd:
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

def vmClone(cvm,count,pat,wait,pd):
    ssh = "ssh "+cvm+" -l nutanix"
    acli = " /usr/local/nutanix/bin/acli -y"
    delVmbyPattern(ssh + acli,cvm,pat)
    run = ssh +acli+" vm.list | grep \""+pat+"\" | grep -v \"VM name\" "
    output = (os.popen(run).read()).split('\n')
    random.shuffle(output)
    try:
        for i in range(count):
            if output[i]:
                (vm,uuid) = output[i].split()
                createNestedCl(ssh+acli,vm,count)
        if pd:
            pdCreates(cvm,patern,"")
    except Exception as e:
        print "Clone create failed "
    time.sleep(wait)


def vgCreate(ssh,container,nodisk,vdsize,pat):
    print "Create a VG -->"
    vgName = "testVG"+pat+str(random.randint(100,128908))
    cmd = ssh+" vg.create "+vgName
    print cmd
    os.system(cmd)
    k=0
    for j in range(0,nodisk):
        #acli vg.disk_create ${prefix}${id} create_size=26G container=dabe
        cmd = ssh+" vg.disk_create "+vgName+" create_size="+vdsize+" container="+container[k]
        print cmd
        os.system(cmd)
        #acli vg.attach_external ${prefix}${id} ${iqn}
        k = k+1 if k < len(container)-1 else 0


def vgLc(cvm,pat,container,nodisk,vgcount,vdsize,wait):
    k=0
    ssh = "ssh "+cvm+" -l nutanix"
    acli = " /usr/local/nutanix/bin/acli -y"

    for i in range(vgcount):
        vgCreate(ssh+acli,container,nodisk,vdsize,pat)

    time.sleep(wait)
    delVgbyPattern(ssh + acli,cvm,pat)


def contCreateDelete(cvm,count,wait,patern):
    k=0
    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    #sp ls |grep 'Id '|awk {'print $3'}|rev|cut -f 1 -d :|rev
    cmd = ncli +" sp ls |grep 'Id '|awk {'print $3'}|rev|cut -f 1 -d :|rev"
    print cmd
    sp_id = os.popen(cmd).read().strip()
    if sp_id:
        sp_id.strip()
        for i in range(count):
            cmd = ncli +" ctr remove name=testReCont_"+patern+"_"+str(i)+" ignore-small-files=true "
            print cmd
            os.system(cmd)
        
        #/home/nutanix/prism/cli/ncli ctr create name=long_test_cont_1 sp-id=$sp_id enable-compression=true compression-delay=0 fingerprint-on-write=on on-disk-dedup=post_process
        for i in range(count):
            cmd = ncli +" ctr create name=testReCont_"+patern+"_"+str(i)+" sp-id="+str(sp_id)+" enable-compression=true compression-delay=0 "
            print cmd
            os.system(cmd)
        
        time.sleep(wait)
        for i in range(count):
            cmd = ncli +" ctr remove name=testReCont_"+patern+"_"+str(i)+" ignore-small-files=true "
            print cmd
            os.system(cmd)


def sshCopyid(ip,userid):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    rsa_key = '\(yes\/no\)\?'
    prompt = "assword:"
    non_rsa='you wanted were added.'

    cmd = "ssh-keygen -R "+str(ip)
    print cmd
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

def main(argv):
    cmd = ''
    tasks = ''
    remote = ''
    pd=0
    paterns = 'gold'
    wait = 1200
    runs = 1
    randomvd = 0
    nofv = 10
    vdisks = 0
    vdsize = "1000G"
    vlan = "vlan0"
    userid = 'nutanix'
    imgp = "ioInt,oltpS,tiltS,fioS,strS,winS,vdbS,xray"
    container = "long_test_cont_1,long_test_cont_2,long_test_cont_3,long_test_cont_4"
    remotesite = ''

    #imgp = '/long_test_cont_1/CentOS7.2.img'
    #container = 'long_test_cont_1'

    try:
        opts, args = getopt.getopt(argv,"hc:d:r:m:t:p:l:w:v:s:n:q:i:g:j:",["cvm=","remote=","container=","imgp=","tasks=","patern=","nofv=","vdisks","wait=","runs=","dsize=","randomvd=","vlan=","pd=","remote-site="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -d <dest/remote server> -r <container> -m <imgp> -t <task vmCreate,vmDelDisk,vmAddDisk,vmMigrate,vmClone,delVmbyPattern,vmCreateDelete,pdCreates > -i <vlan> -l <no of vms> -v <vdisks> -s <vdsize> -n <no of runs> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -d <dest/remote server> -r <container> -m <imgp> -t <task vmCreate,vmDelDisk,vmAddDisk,vmMigrate,delVmbyPattern,vmCreateDelete,pdCreates > -l <no of vms> -v <vdisks> -s <vdsize> -q <random vdisk size> -n <no of runs> -i <vlan> -w <wait>'
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
        elif opt in ("-i", "--vlan"):
            vlan = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)
        elif opt in ("-n", "--runs"):
            runs = int(arg)
        elif opt in ("-g", "--pd"):
            pd = int(arg)
        elif opt in ("-q", "--randomvd"):
            randomvd = int(arg)
        elif opt in ("-j", "--remote-site"):
            remotesite = arg

    cvml = remotesite.split(',')
    print remotesite
    print cvml 

    #setupRemote(cvml,'10')
    #sys.exit()
    sshCopyid(cvm,"nutanix")
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    cvmips =get_svmips(cvm)
#    for  cvmip in cvmips:
#        sshCopyid(cvmip,"nutanix")

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
        runS(ssh+acli,cvm,container,imgp,hostplist,tasks,nofv,vdisks,paterns,vdsize,randomvd,vlan,wait,remote,pd)
        if i<1:
            time.sleep(wait)

def runS(ssh,cvm,container,imgp,hostlist,tasks,vmcount,vdisks,paterns,edisksize,randomvd,vlan,wait,remote,pd):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    sshCopyid(cvm,"nutanix")
    vcpus = 4
    bdisksize = '8G'
    #vmcount = 40
    count = 12
    for (task,patern) in itertools.izip(tasks,paterns):
        if task == 'vmCreate':
            vmCreate(ssh,cvm,vmcount,patern,bdisksize,vcpus,vdisks,hostlist,container,edisksize,randomvd,imgp,userid,vlan,remote,pd)
        elif task == 'vmSnC':
            vmSnC(ssh,cvm,vmcount,bdisksize,vcpus,vdisks,hostlist,container,edisksize,randomvd,imgp,userid,remote,vlan,wait,pd)
        elif task == 'vmCreateLarge':
            img=["vgcS"]
            edisksz="25000g"
            vdisk=1
            vmCreateLarge(ssh,cvm,vmcount,patern,bdisksize,vcpus,vdisk,hostlist,container,edisksz,img,userid,vlan,remote,pd)
        elif task == 'vmCreateSmall':
            vmcnt=100
            vmCreateSmall(ssh,cvm,vmcnt,patern,hostlist,container,userid,vlan,remote,pd)
        elif task == 'vmAddDisk':
            vmAddDisk(ssh,patern,edisksize,container)
        elif task == 'vmMigrate':
            vmMigrate(ssh,patern,count,hostlist,wait)
        elif task == 'vmClone':
            vmClone(cvm,count,patern,wait,pd)
        elif task == 'delVmbyPattern':
            delVmbyPattern(ssh,cvm,patern)
        elif task == 'contCreateDelete':
            contCreateDelete(cvm,vmcount,wait,patern)
        elif task == 'vmCreateDelete':
            vmCreateDelete(ssh,count,wait,patern,edisksize,container)
        elif task == 'vmDelDisk':
            vmDelDisk(ssh,patern)
        elif task == 'vgLc':
            vgLc(cvm,patern,container,vdisks,vmcount,edisksize,wait)
        elif task == 'pdCreates':
            pdCreates(cvm,patern,remote)
        elif task == 'delPdbyPattern':
            delPdbyPattern(ssh,cvm,patern)
        time.sleep(wait)


if __name__ == "__main__":
    main(sys.argv[1:])


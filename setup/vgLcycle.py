#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import itertools


def vmCreate(cvm,image,vlan):
    ssh = "ssh "+cvm+" -l nutanix"
    acli = " /usr/local/nutanix/bin/acli -y"
    run = ssh+acli
    memory='8G'
    vdisks=6
    vdisk_size = '20G'
    vcpu=2
    cores=2
    #vm.create long_run_vm_2 memory=8G num_vcpus=4
    vmname = "vgclient_"+image+"_vm_"+str(random.randint(100,128908))
    cmd = run+ " vm.create "+vmname+" memory="+memory+" num_vcpus="+str(vcpu)+" num_cores_per_vcpu="+str(cores)
    print cmd
    os.system(cmd)
    cmd = run+" vm.disk_create "+vmname+" clone_from_image="+image
    print cmd
    os.system(cmd)
    #vm.nic_create testVM network=vlan0
    cmd =run+ " vm.nic_create "+vmname+" network="+vlan
    print cmd
    os.system(cmd)
    cmd = run+" vm.on "+vmname
    print cmd
    os.system(cmd)
    time.sleep(60)
    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    run = ncli+" vm list name="+vmname+" | grep \"VM IP Addresses\""
    print run
    match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
    if match is not None:
        ip = match.group()
        print vmname+"  "+ip 
        return (ip,vmname)
    else :
        cmd = ssh+acli+" vm.power_cycle "+vmname
        print cmd
        os.system(cmd)
        time.sleep(120)
        run = ncli+" vm list name="+vmname+" | grep \"VM IP Addresses\""
        print run
        match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
        if match is not None:
            ip = match.group()
            print vmname+"  "+ip
            return (ip,vmname)
    return("none","none")

def vgCreate(ssh,ncli,container,init,pat,nodisk,vgcount,vdsize):
    print "Create a VG -->"
    for i in range(vgcount):
        vgName = pat+str(random.randint(100,128908))
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

def vgAttach(ssh,init,pat):
        cmd = ssh+" vg.list | grep "+pat
        print cmd
        output = (os.popen(cmd).read()).split('\n')
        for i in range(0,len(output)-1):
            (vg,uuid) = output[i].split()
            cmd = ssh+" vg.attach_external "+vg+" initiator_name="+init
            print cmd
            os.system(cmd)
       


def vgDel(ssh,ncli,vgReg):
    print "Delete VG ---> "
    for pat in vgReg:
        cmd = ssh+" vg.list | grep "+pat
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
            if 0:
                try:
                    cmd = ncli +" pd list | grep testVG"
                    print cmd
                    output = (os.popen(cmd).read()).split('\n')
                    for pd in output:
                        pds = (pd.split(':')[1]).strip()
                        cmd = ncli +"pd clear-schedules name="+pds
                        print cmd
                        os.system(cmd)
                        cmd = ncli + " pd rm-snap name="+pds+" clear-all=true "
                        print cmd
                        os.system(cmd)
                        cmd = ncli +" pd unprotect name="+pds+" volume-group-uuids="+uuid
                        print cmd
                        os.system(cmd)
                        cmd = ncli + " pd remove name="+pds
                        print cmd
                        os.system(cmd)
                except Exception as e:
                    print op 


def pdCreate(ssh,run,nosnap):
    cmd = ssh+" vg.list | grep testVG"
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    for i in range(0,len(output)-1):
        (vm,uuid) = output[i].split()
        cmd = run +" pd create name=testPD_"+vm
        print cmd
        os.system(cmd)
        cmd = run +" pd protect name=testPD_"+vm+" volume-group-uuids="+uuid+" cg-name=testCG"+vm
        print cmd
        os.system(cmd)
        cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
        print cmd
        os.system(cmd)
        cmd = run +"\" pd add-hourly-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" every-nth-hour=6 start-time=\\\"02/14/2018 18:30:00 UTC\\\"\""
        print cmd
        os.system(cmd)
        cmd = run +"\" pd add-daily-schedule name=testPD_"+vm+" local-retention="+str(nosnap)+" start-time=\\\"02/14/2018 09:30:00 UTC\\\"\""
        print cmd
        os.system(cmd)


def discoverLun(ncli,init):
    cmd = ncli+" cluster get-params | grep \"External Data Services\"" 
    print cmd
    idp = (os.popen(cmd).read()).split(':')[1]
    idp = idp.strip()
    cmd = "ssh "+init+" -l nutanix \"sudo iscsiadm -m node --logout \""
    print cmd
    os.system(cmd)
    cmd = "ssh "+init+" -l nutanix \"sudo rm -rf /var/lib/iscsi/send_targets/*\""
    print cmd
    os.system(cmd)
    cmd = "ssh "+init+" -l nutanix \"sudo iscsiadm --mode node -o delete \""
    print cmd
    os.system(cmd)
    cmd = "ssh "+init+" -l nutanix \"sudo iscsiadm --mode discoverydb --portal "+idp+":3260 --op delete --type sendtargets\""
    print cmd
    os.system(cmd)
    cmd = "ssh "+init+" -l nutanix \"sudo iscsiadm -m discoverydb --portal "+idp+":3260 -t sendtargets -o new \""
    print cmd
    os.system(cmd)
    cmd = "ssh "+init+" -l nutanix \"sudo iscsiadm -m discoverydb --portal "+idp+":3260 -t sendtargets -o update --discover \""
    print cmd
    os.system(cmd)
    cmd = "ssh "+init+" -l nutanix \"sudo iscsiadm -m node --login \""
    print cmd
    os.system(cmd)

def configVg(init,fsize):
    devList = []
    cmd = "ssh "+init+" -l nutanix \"/usr/bin/lsblk -S -f -s | grep -v rom\""
    output = (os.popen(cmd).read()).split('\n')
    for i in range(1,len(output)-1):
        if 'ext4' not in output[i] :
            line = output[i].split()
            devList.append("/dev/"+line[0])

    listToStr = ' '.join([str(elem) for elem in devList]) 
    cmd = "ssh "+init+" -l nutanix \" sudo pvcreate "+listToStr+" \""
    print cmd
    os.system(cmd)

    bs = ["128M","64M","32M","16M","8M"]
    alloc = ["cling","anywhere","contiguous"]

    l=i=j=k=0
    while i < len(devList)-1:
        listToStr = ' '.join([str(elem) for elem in devList[i:i+3]])
        cmd = "ssh "+init+" -l nutanix \" sudo vgcreate -s "+bs[j]+" --alloc "+alloc[k]+" vol_grp"+str(l)+" "+listToStr +"\""
        print cmd
        os.system(cmd)
        time.sleep(30)
        cmd = "ssh "+init+" -l nutanix \" sudo lvcreate -L "+fsize+" -i 3 -I "+bs[j]+" -n my_lv"+str(l)+" vol_grp"+str(l)+" \""
        print cmd
        os.system(cmd)
        time.sleep(30)

        #cmd = "ssh "+init+" -l nutanix \"sudo mkfs.ext4 /dev/vol_grp"+str(l)+"/my_lv"+str(l)+";sudo mkdir /my_vol"+str(l)+";sudo mount -t ext4 /dev/vol_grp"+str(l)+"/my_lv"+str(l)+" /my_vol"+str(l)+" \""
        #print cmd
        #os.system(cmd)

        #run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/zombFileMulN1 pathname=/my_vol"+str(l)+" fs=100K bs=10K nc=1000000 </dev/null>/dev/null 2>&1 &\""
        #print run
        #os.system(run)
        #run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/fop -H 0 -W 0 -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd -s 100g -t 15 -n 1 /my_vol"+str(l)+" </dev/null>/dev/null 2>&1 &\""
        #print run
        #os.system(run)
        #run = "ssh "+init+" -l nutanix \" sudo /home/nutanix/clSc/fop -H 2 -W 10,100,500,1000  -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd  -f 10k,20,20,10 -n 300 -s 10k,20,10k,100k -t 10 -O RD /my_vol"+str(l)+" </dev/null>/dev/null 2>&1 &\""
        #print run
        #os.system(run)
 
        j =  j+1 if j < len(bs)-1 else 0
        k = k+1 if k < len(alloc)-1 else 0
        l +=1 
        i +=3
         
def sshCopyid(ip,user):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    cmd = "ssh-keygen -R "+str(ip)
    os.system(cmd)
    try :
        rsa_key = '\(yes\/no\)\?'
        prompt = "assword:"
        no_rsa = 'you wanted were added.'
        cmd = " /usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@"+str(ip)
        print cmd
        child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no %s@%s'%(user,ip))
        r = child.expect([no_rsa,prompt,""])
        #=child.expect ('you wanted were added.')
        print "Outp"+str(r)
        if r==1:
            cmd = " ssh "+str(ip)+" nutanix -l pwd"
            print cmd
            child = pexpect.spawn('ssh %s %s -l pwd'%(ip,user))
            i = child.expect([rsa_key,prompt,""])
            if i==0:
                child.sendline('yes')
                child.expect(prompt)
                child.sendline(passwd)
            elif i==1:
                child.sendline(passwd)
            else:
                child.sendline(passwd)
        else :
                child.expect(prompt)
                child.sendline(passwd)
        child.interact()
        child.close()
    except Exception as e:
        print "Oops Something went wrong buddy"
        #print e

def sshCopyids(ip,user):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    try :
        cmd = "ssh-keygen -R "+str(ip)+"; ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o \"StrictHostKeyChecking no\" "+user+"@"+str(ip)
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

def cofigClient(dest,image,vlan):
    userid = 'nutanix'
    (init,vm) = vmCreate(dest,image,vlan)
    if vm != "none":
        sshCopyid(init,"root")
        sshCopyid(init,userid)
        cmd = "ssh "+init+" -l root rm -rf /etc/iscsi/initiatorname.iscsi "
        print cmd
        os.system(cmd)
        cmd = "ssh "+init+" -l root \"/usr/sbin/iscsi-iname\" "
        print cmd
        iqn = (os.popen(cmd).read()).strip()
        # "echo \"InitiatorName=iqn.1994-05.com.redhat:2b86a0104dfd\" > /etc/iscsi/initiatorname.iscsi"
        cmd = "ssh "+init+" -l root \"echo \\\"InitiatorName="+iqn+"\\\" > /etc/iscsi/initiatorname.iscsi \" "
        print cmd
        os.system(cmd)
        print "IQN of the init --> "+iqn
        #cmd = "scp -r /home/santoshkumar.ladi/scripts/clSc nutanix@"+init+":/home/nutanix"
        #print cmd
        #os.system(cmd)
        return(iqn,init,vm) 
    return None

def main(argv):
    cmd = ''
    dest = ''
    nodisk = 1
    vgcount = 1
    vmcount = 1
    onlyreg = 1
    vdsize = '1000G'
    fsize = '2.4T'
    wait = 36000
    userid = 'nutanix'
    image = 'vgcS'
    vlan = 'vlan0'
    container = "long_test_cont_1,long_test_cont_2,long_test_cont_3,long_test_cont_4"

    try:
        opts, args = getopt.getopt(argv,"hi:c:l:d:n:x:v:f:m:w:q:o:",["cvm=","containers=","iscsi=","vdsize=","nodisk=","vmcount=","vgcount=","fsize=","image=","wait=","vlan=","onlyreg="])
    except getopt.GetoptError:
        print 'vgSetup.py -i <cvmip> -c <containers> -l <iscsi inti> -d <vdisk size> -n<no of disks> -v <vgcount> -f <file system size> -q <vlan> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'vgSetup.py -i <cvmip> -c <containers> -l <iscsi inti> -d <vdisk size> -n<no of disks> -v <vgcount> -f <file system size> -q <vlan> -w <wait>'
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvm = arg
        elif opt in ("-c", "--container"):
            container = arg
        elif opt in ("-l", "--iscsi"):
            dest = arg
        elif opt in ("-n", "--nodisk"):
            nodisk = int(arg)
        elif opt in ("-v", "--vgcount"):
            vgcount = int(arg)
        elif opt in ("-x", "--vmcount"):
            vmcount = int(arg)
        elif opt in ("-d", "--vdsize"):
            vdsize = arg
        elif opt in ("-f", "--fsize"):
            fsize = arg
        elif opt in ("-m", "--image"):
            image = arg
        elif opt in ("-q", "--vlan"):
            vlan = arg
        elif opt in ("-o", "--onlyreg"):
            onlyreg = int(arg)
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm,userid)
    container = container.split(',')

    sshCopyid(dest,userid)
    while 1:
        cmd = "pgrep -f vgStress.py | xargs sudo kill"
        print cmd
        os.system(cmd)
        runS(cvm,dest,container,nodisk,vmcount,vgcount,vdsize,fsize,image,vlan,onlyreg,wait)
        time.sleep(wait)


def runS(cvm,dest,container,nodisk,vmcount,vgcount,vdsize,fsize,image,vlan,onlyreg,wait):
    vmList=[]
    vgReg=[]
    ssh = "ssh "+cvm+" -l nutanix"
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    run = "ssh "+dest+" -l nutanix "+acli
    try :
        cmd = "ssh "+dest+" -l nutanix "+acli+" vm.delete vg\*"
        print cmd
        os.system(cmd)
        vgDel(ssh+acli,ncli,vgReg)
        for i in range (vmcount) :
            (iqn,init,vm) = cofigClient(dest,image,vlan) 
            vmList.append(vm)
            if not iqn :
                sys.exit()

            vgName = "testVG"+str(random.randint(100,128908))
            vgCreate(ssh+acli,ncli,container,iqn,vgName,nodisk,vgcount,vdsize)
            time.sleep(60)
            vgAttach(ssh+acli,iqn,vgName)
            cmd = "/home/santoshkumar.ladi/scripts/setup/vgStress.py -c "+cvm+" -i "+init+" -g "+vgName+" -f "+fsize+" -d "+vdsize+" -o "+str(onlyreg)+" -r 0 -w "+str(wait)+" &" 
            print cmd
            os.system(cmd)
            vgReg.append(vgName)
        #pdCreate(ssh+acli,ncli,10)
    
        time.sleep(3600)
        vgDel(ssh+acli,ncli,vgReg)
        for vm in vmList:
            cmd = "ssh "+dest+" -l nutanix "+acli+" vm.delete "+vm
            print cmd
            os.system(cmd)
    except Exception as e:
        print "Error --> "+str(vmList)
        print  e.message, e.args 

if __name__ == "__main__":
    main(sys.argv[1:])


#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import itertools


def generate_random_string():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(1024))


def updateVmbyPattern(ssh,cvm,vmList):
    for vm in vmList:
        cmd = ssh+" vm.update "+str(vm["name"])+" name="+str(vm["name"])+"testInitVg"+str(generate_random_string())
        print cmd
        os.system(cmd)

def updateVgbyPattern(ssh,cvm,vgame):
    run = ssh+" vg.list | grep -v auto | grep -v ltss | grep -E \""+vgame+"|update\" "
    print run
    output = (os.popen(run).read()).split('\n')
    print output

    for i in range(0,len(output)-1):
        #VM name  VM UUID
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        (vg,uuid) = output[i].split()
        cmd = ssh+" vg.update "+vg+" name=update"+vg+str(generate_random_string())
        print cmd
        os.system(cmd)

def getVMs(cvm,count,pat):
    vmList = []
    ssh = "ssh "+cvm+" -l nutanix"
    acli = " /usr/local/nutanix/bin/acli -y"
    run = ssh +acli+" vm.list power_state=on | grep -v auto | grep -v ltss | grep \""+pat+"\" | grep -v \"VM name\" "
    print run
    output = (os.popen(run).read()).split('\n')
    print output
    if len(output) <= 1:
        run = ssh +acli+" vm.list power_state=on | grep -v auto | grep -v ltss | grep -v \"VM name\" "
        print run
        output = (os.popen(run).read()).split('\n')
        print output

    random.shuffle(output)
    for i in range(count):
        if output[i]:
            try:
                (vmname,uuid) = output[i].split()
                ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
                run = ncli+" vm list name="+vmname+" | grep \"VM IP Addresses\""
                print run
                match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
                if match is not None:
                    ip = match.group()
                    print vmname+"  "+ip
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
                if not ip :
                    continue
                sshCopyid(ip)
                cmd = "ssh "+ip+" -l nutanix cat /etc/iscsi/initiatorname.iscsi"
                iqn = (os.popen(cmd).read()).split('=')[1]
                print "IQN of the init --> "+iqn
                if not iqn :
                    sys.exit()
                else:
                    vmList.append({"name":vmname,"ip":ip,"iqn":iqn})
            except Exception as e:
                print "Attach failed  "
                count=count+1
        return vmList


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
        cmd = ssh+" vg.delete "+uuid
        print cmd
        os.system(cmd)

def vgCreate(ssh,container,init,nodisk,vgcount,vdsize):
    print "Create a VG -->"
    vgList = []
    for i in range ( 0,vgcount):
        vgName = "testInitVg"+str(random.randint(100,128908))
        cmd = ssh+" vg.create "+vgName
        print cmd
        os.system(cmd)
        vgList.append(vgName)
        k=0
        for j in range(0,nodisk):
            #acli vg.disk_create ${prefix}${id} create_size=26G container=dabe
            cmd = ssh+" vg.disk_create "+vgName+" create_size="+vdsize+" container="+container[k] 
            print cmd
            os.system(cmd)
            #acli vg.attach_external ${prefix}${id} ${iqn}
            k = k+1 if k < len(container)-1 else 0
         
        cmd = ssh+" vg.attach_external "+vgName+" initiator_name="+init
        print cmd
        os.system(cmd)
    return vgList

def discoverLun(ncli,init):
    try :
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
    except Exception as e:
        print "error in discoverLun"+str(e)
        return 0 

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
        try:
            cmd = "ssh "+init+" -l nutanix \" sudo vgcreate -s "+bs[j]+" --alloc "+alloc[k]+" vol_grp"+str(l)+" "+listToStr +"\""
            print cmd
            os.system(cmd)
            #time.sleep(30)
            cmd = "ssh "+init+" -l nutanix \" sudo lvcreate -L "+fsize+" -i 3 -I "+bs[j]+" -n my_lv"+str(l)+" vol_grp"+str(l)+" \""
            print cmd
            os.system(cmd)
            #time.sleep(30)
        except Exception as e:
            print "Oops Something went wrong buddy"
            break

        j =  j+1 if j < len(bs)-1 else 0
        k = k+1 if k < len(alloc)-1 else 0
        l +=1 
        i +=3
         
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
    cmd = ''
    init = ''
    nodisk = 2
    vgcount = 200
    novol = 5
    vdsize = '10G'
    fsize = '20G'
    wait = 1200
    runtr = 1
    userid = 'nutanix'
    container = "long_test_cont_1,long_test_cont_2,long_test_cont_3,long_test_cont_4"

    try:
        opts, args = getopt.getopt(argv,"hi:c:b:p:d:n:v:f:r:w:",["cvm=","containers=","novol=","pattern=","vdsize=","nodisk=","vgcount=","fsize=","runtr=","wait="])
    except getopt.GetoptError:
        print 'vgInitStress.py -i <cvmip> -c <containers> -p <pattern> -d <vdisk size> -n<no of disks> -v <vgcount> -s <file system size> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'vgInitStress.py -i <cvmip> -c <containers> -p <pattenrs> -d <vdisk size> -n<no of disks> -v <vgcount> -s <file system size> -w <wait>'
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvm = arg
        elif opt in ("-c", "--container"):
            container = arg
        elif opt in ("-p", "--pattern"):
            pattern = arg
        elif opt in ("-n", "--nodisk"):
            nodisk = int(arg)
        elif opt in ("-v", "--vgcount"):
            vgcount = int(arg)
        elif opt in ("-d", "--vdsize"):
            vdsize = arg
        elif opt in ("-f", "--fsize"):
            fsize = arg
        elif opt in ("-b", "--novol"):
            novol = arg
        elif opt in ("-r", "--runtr"):
            runtr = int(arg)
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    container = container.split(',')
    for i in range(vgcount):
        vmList = getVMs(cvm,novol,pattern)
        for vm in vmList:
            print vm["name"],vm["ip"],vm["iqn"]
            runS(ssh+acli,cvm,container,vm["ip"],vm["iqn"],vm["name"],nodisk,vgcount,vdsize,fsize,runtr,wait)
        time.sleep(wait)
        updateVgbyPattern(ssh+acli,cvm,"testInitVg")
        time.sleep(wait)
        updateVmbyPattern(ssh+acli,cvm,vmList)
        time.sleep(wait)
        delVgbyPattern(ssh+acli,cvm,"testInitVg")


def runS(ssh,cvm,container,init,iqn,vmname,nodisk,vgcount,vdsize,fsize,runtr,wait):
    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    acli = "ssh "+cvm+" -l nutanix /usr/local/nutanix/bin/acli -y"
    vgList = vgCreate(ssh,container,iqn,nodisk,vgcount,vdsize)
    for i in range(vgcount):
        #cmd = acli+" vm.power_cycle "+vmname
        #print cmd
        #os.system(cmd)
        discoverLun(ncli,init)
    if runtr:
        configVg(init,fsize)

if __name__ == "__main__":
    main(sys.argv[1:])


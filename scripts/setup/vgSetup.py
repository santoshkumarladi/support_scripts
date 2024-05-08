#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import itertools


def vgCreate(ssh,container,init,nodisk,vgcount,vdsize):
    print "Create a VG -->"
    vgList = []
    for i in range ( 0,vgcount):
        vgName = "testVG"+str(random.randint(100,128908))
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
        cmd = "ssh "+init+" -l nutanix \"sudo mkfs.ext4 /dev/vol_grp"+str(l)+"/my_lv"+str(l)+";sudo mkdir /my_vol"+str(l)+";sudo mount -t ext4 /dev/vol_grp"+str(l)+"/my_lv"+str(l)+" /my_vol"+str(l)+" \""
        print cmd
        os.system(cmd)

        run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/zombFileMulN1 pathname=/my_vol"+str(l)+" fs=100K bs=10K nc=1000000 </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
        run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/fop -H 0 -W 0 -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd -s 100g -t 15 -n 1 /my_vol"+str(l)+" </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
        run = "ssh "+init+" -l nutanix \" sudo /home/nutanix/clSc/fop -H 2 -W 10,100,500,1000  -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd  -f 10k,20,20,10 -n 300 -s 10k,20,10k,100k -t 10 -O RD /my_vol"+str(l)+" </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
 
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
    nodisk = 6
    vgcount = 1
    vdsize = '1000G'
    fsize = '2.4T'
    wait = 1200
    userid = 'nutanix'
    container = "long_test_cont_1,long_test_cont_2,long_test_cont_3,long_test_cont_4"

    try:
        opts, args = getopt.getopt(argv,"hi:c:l:d:n:v:f:w:",["cvm=","containers=","iscsi=","vdsize=","nodisk=","vgcount=","fsize=","wait="])
    except getopt.GetoptError:
        print 'vgSetup.py -i <cvmip> -c <containers> -l <iscsi inti> -d <vdisk size> -n<no of disks> -v <vgcount> -s <file system size> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'vgSetup.py -i <cvmip> -c <containers> -l <iscsi inti> -d <vdisk size> -n<no of disks> -v <vgcount> -s <file system size> -w <wait>'
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvm = arg
        elif opt in ("-c", "--container"):
            container = arg
        elif opt in ("-l", "--iscsi"):
            init = arg
        elif opt in ("-n", "--nodisk"):
            nodisk = int(arg)
        elif opt in ("-v", "--vgcount"):
            vgcount = int(arg)
        elif opt in ("-d", "--vdsize"):
            vdsize = arg
        elif opt in ("-f", "--fsize"):
            fsize = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    container = container.split(',')
    sshCopyid(init)
    cmd = "ssh "+init+" -l"+userid+" cat /etc/iscsi/initiatorname.iscsi"
    iqn = (os.popen(cmd).read()).split('=')[1]
    print "IQN of the init --> "+iqn

    if not iqn :
        sys.exit()
    cmd = "scp -r /home/santoshkumar.ladi/scripts/clSc nutanix@"+init+":/home/nutanix"
    print cmd
    os.system(cmd)

    runS(ssh+acli,cvm,container,init,iqn,nodisk,vgcount,vdsize,fsize,wait)
    time.sleep(wait)


def runS(ssh,cvm,container,init,iqn,nodisk,vgcount,vdsize,fsize,wait):
    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    vgList = vgCreate(ssh,container,iqn,nodisk,vgcount,vdsize)
    discoverLun(ncli,init)
    configVg(init,fsize)

if __name__ == "__main__":
    main(sys.argv[1:])


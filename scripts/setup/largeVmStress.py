#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import subprocess




def vmCreate(cvm,pat,image):
    ssh = "ssh "+cvm+" -l nutanix"
    acli = " /usr/local/nutanix/bin/acli -y"
    run = ssh+acli
    memory='20G'
    vdisks=8
    vdisk_size = '20G'
    vcpu=4
    cores=2
    #vm.create long_run_vm_2 memory=8G num_vcpus=4
    vmname = "vgclient_"+image+"_"+pat+str(random.randint(100,128908))
    cmd = run+ " vm.create "+vmname+" memory="+memory+" num_vcpus="+str(vcpu)+" num_cores_per_vcpu="+str(cores)
    print cmd
    os.system(cmd)
    cmd = run+" vm.disk_create "+vmname+" clone_from_image="+image
    print cmd
    os.system(cmd)
    #vm.nic_create testVM network=vlan0
    cmd =run+ " vm.nic_create "+vmname+" network=vlan0"
    print cmd
    os.system(cmd)
    cmd = run+" vm.on "+vmname
    print cmd
    os.system(cmd)
    time.sleep(60)
    ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
    run = ssh+" "+ncli+" vm list name="+vmname+" | grep \"VM IP Addresses\""
    print run
    match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
    if match is not None:
        ip = match.group()
        print vmname+"  "+ip
        return (ip,vmname)
    else :
        time.sleep(120)
        run = ssh+" "+ncli+" vm list name="+vmname+" | grep \"VM IP Addresses\""
        print run
        match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
        if match is not None:
            ip = match.group()
            print vmname+"  "+ip
            return (ip,vmname)

def cofigClient(dest,cvm,pat,vgName,image):
    acli = "ssh "+cvm+ " -l nutanix /usr/local/nutanix/bin/acli -y"
    userid = 'nutanix'
    (init,vm) = vmCreate(dest,pat,image)
    time.sleep(60)
    sshCopyid(init,"root")
    time.sleep(60)
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
    cmd = acli+" vg.attach_external "+vgName+" initiator_name="+iqn
    print cmd
    os.system(cmd)

    return(iqn,init,vm)


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

def cleanCong(init,dsize):
    devList = []
    listToStr =''

    cmd = "ssh "+init+" -l nutanix \"pgrep -f my_vol | xargs sudo kill\""
    print cmd
    os.system(cmd)
    cmd = "ssh "+init+" -l nutanix \"pgrep -f fio | xargs sudo kill\""
    print cmd
    os.system(cmd)
    cmd = "ssh "+init+" -l nutanix \"mount | grep my_vol \""
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    for i in (output):
        if i:
            cmd = "ssh "+init+" -l nutanix \" sudo umount "+i.split()[2]+"\""
            print cmd
            os.system(cmd)

    cmd = "ssh "+init+" -l nutanix \"sudo rm -rf /my_vol* \""
    print cmd
    os.system(cmd)
    cmd = "ssh "+init+" -l nutanix \"sudo systemctl restart lvm2-lvmetad.service \""
    print cmd
    os.system(cmd)

    cmd = "ssh "+init+" -l nutanix \"sudo systemctl restart iscsid.service  \""
    print cmd
    os.system(cmd)
    time.sleep(30)
    cmd = "ssh "+init+" -l nutanix \"/usr/bin/lsblk -S -f -s --output NAME,FSTYPE,SIZE,TYPE | grep -v rom | grep "+dsize+"\""
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    print output
    for i in range(0,len(output)-1):
        if 'ext4' not in output[i] :
            line = output[i].split()
            devList.append("/dev/"+line[0])

    if not output:
        sys.exit()

    listToStr = ' '.join([str(elem) for elem in devList])


    cmd = "ssh "+init+" -l nutanix \" sudo lvdisplay | grep my_lv | grep \\\"LV Path\\\" \" "
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    if output :
        for i in range(len(output)-1):
            cmd = "ssh "+init+" -l nutanix \" sudo lvremove -f "+output[i].split()[2]+"\""
            print cmd
            os.system(cmd)
    cmd = "ssh "+init+" -l nutanix \" sudo vgdisplay | grep vol_grp \" "
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    if output :
        for i in range(len(output)-1):
            cmd = "ssh "+init+" -l nutanix \" sudo vgremove vol_grp"+str(i)+"\""
            print cmd
            os.system(cmd)

    cmd = "ssh "+init+" -l nutanix \" sudo pvremove "+listToStr+" --force --force \""
    print cmd
    os.system(cmd)
    time.sleep(30)

    cmd = "ssh "+init+" -l nutanix \" sudo wipefs -a "+listToStr+"  \""
    print cmd
    os.system(cmd)

def getSize(fsize):
    cmd="numfmt --from=iec "+fsize
    op = os.popen(cmd).read()
    op = op.strip()
    print "The file system size "+str(op)
    return op

def configVg(init,fsize,dsize):
    devList = []
    cmd = "ssh "+init+" -l nutanix \"/usr/bin/lsblk -S -f -s --output NAME,FSTYPE,SIZE,TYPE | grep -v rom | grep "+dsize+"\""
    #cmd = "ssh "+init+" -l nutanix \"/usr/bin/lsblk -S -f -s | grep -v rom\""
    output = (os.popen(cmd).read()).split('\n')
    print output
    for i in range(0,len(output)-1):
        if 'ext4' not in output[i] :
            line = output[i].split()
            devList.append("/dev/"+line[0])

    if not output:
        cmd = "ssh "+init+" -l nutanix \"/usr/bin/lsblk -S -f -s --output NAME,FSTYPE,SIZE | grep -v rom \""
        output = (os.popen(cmd).read()).split('\n')
        print cmd
        os.system(cmd)
        sys.exit()

    listToStr = ' '.join([str(elem) for elem in devList]) 
    cmd = "ssh "+init+" -l nutanix \" sudo pvcreate "+listToStr+" \""
    print cmd
    os.system(cmd)

    bs = ["128M","64M","32M","16M","8M"]
    alloc = ["anywhere","contiguous","cling"]
    nodisk_per_fs = int(getSize(fsize))//int(getSize(dsize))
    nodisk_per_fs += 1
    print "Diskz per FS -> "+str(nodisk_per_fs)
    
    l=i=j=k=0
    while i < len(devList)-1:
        listToStr = ' '.join([str(elem) for elem in devList[i:i+nodisk_per_fs]])
        try :
            cmd = "ssh "+init+" -l nutanix \" sudo vgcreate -s "+bs[j]+" --alloc "+alloc[k]+" vol_grp"+str(l)+" "+listToStr +"\""
            print cmd
            if os.system(cmd) != 0 :
                raise Exception('Cmd failed!')
            time.sleep(60)
            cmd = "ssh "+init+" -l nutanix \" sudo lvcreate -l 100%VG -i 3 -I "+bs[j]+" -n my_lv"+str(l)+" vol_grp"+str(l)+" -y -Wy -Zy \""
            print cmd
            if os.system(cmd) != 0 :
                raise Exception('Cmd failed!')
            time.sleep(60)
            cmd = "ssh "+init+" -l nutanix \"sudo mkfs.ext4 /dev/vol_grp"+str(l)+"/my_lv"+str(l)+";sudo mkdir /my_vol"+str(l)+";sudo mount -t ext4 /dev/vol_grp"+str(l)+"/my_lv"+str(l)+" /my_vol"+str(l)+" \""
            print cmd
            if os.system(cmd) != 0 :
                raise Exception('Cmd failed!')
        except :
            print "Config part failed check the init and start again "
            sys.exit()

        run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/zombFileMulN1 pathname=/my_vol"+str(l)+" fs=1000K bs=10K nc=1000000 </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
        run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/fop -H 4 -W 4 -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd -s 10000M -t 15 -n 1 /my_vol"+str(l)+" </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
        run = "ssh "+init+" -l nutanix \" sudo /home/nutanix/clSc/fop -H 4 -W 4 -W 10,100,500,1000  -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd  -f 10k,20,20,10 -n 300 -s 10k,20,10k,100k -t 10 -O RD /my_vol"+str(l)+" </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
        run = "ssh "+init+" -l nutanix \"sudo dd if=/dev/urandom of=/my_vol"+str(l)+"/testFile"+str(l)+" bs=1M count=10000 </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
        run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/zombFileMulCnt pathname=/my_vol"+str(l)+" fs=100K bs=10K nc=1000000 rm=0 </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
        # ./smallFiles pathname=<name of the dir> bs=<block size> sz=<file size> nf=<no of files>
        run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/smallFiles pathname=/my_vol"+str(l)+" sz=1K bs=1K nf=1000000 </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
        #Usage: ./lotSmall pathname=<name of the dir> bs=<block size> sz=<file size> nf=<no of files>
        run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/lotSmall pathname=/my_vol"+str(l)+" sz=1K bs=1K nf=1000000 </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
        run = "ssh "+init+" -l nutanix \"sudo cp -rf /home/nutanix/dst.1597252208 /my_vol"+str(l)+"/testBigFile"+str(l)+"\""
        print run
        os.system(run)
        #Usage: ./createLargeF srcpath=<src file> dstpath=<dst file> bs=<block size> dfs=<destination filesize> rd=<random copy> 
        run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/createLargeF srcpath=/my_vol"+str(l)+"/testBigFile"+str(l)+" dstpath=/my_vol"+str(l)+" bs=1M dfs="+fsize+" rd=0 </dev/null>/dev/null 2>&1 &\""
        print run
        os.system(run)
 
        j =  j+1 if j < len(bs)-1 else 0
        k = k+1 if k < len(alloc)-1 else 0
        l +=1 
        i +=nodisk_per_fs
      

def onlyStress(init,fsize):
    l=0
    cmd = "ssh "+init+" -l nutanix \"pgrep -f my_vol | xargs sudo kill\""
    print cmd
    os.system(cmd)

    cmd = "ssh "+init+" -l nutanix \"mount | grep my_vol \""
    print cmd
    output = (os.popen(cmd).read()).split('\n')
    for i in (output):
        if i:
            run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/zombFileMulN1 pathname="+i.split()[2]+" fs=1000K bs=10K nc=1000000 </dev/null>/dev/null 2>&1 &\""
            print run
            os.system(run)
            run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/fop -H 4 -W 4 -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd -s 10000M -t 15 -n 1 "+i.split()[2]+" </dev/null>/dev/null 2>&1 &\""
            print run
            os.system(run)
            run = "ssh "+init+" -l nutanix \" sudo /home/nutanix/clSc/fop -H 4 -W 4 -W 10,100,500,1000  -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd  -f 10k,20,20,10 -n 300 -s 10k,20,10k,100k -t 10 -O RD "+i.split()[2]+" </dev/null>/dev/null 2>&1 &\""
            print run
            os.system(run)
            run = "ssh "+init+" -l nutanix \"sudo dd if=/dev/urandom of="+i.split()[2]+"/testFile"+str(l)+" bs=1M count=10000 </dev/null>/dev/null 2>&1 &\""
            print run
            os.system(run)
            run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/zombFileMulCnt pathname="+i.split()[2]+" fs=100K bs=10K nc=1000000 rm=0 </dev/null>/dev/null 2>&1 &\""
            print run
            os.system(run)
            # ./smallFiles pathname=<name of the dir> bs=<block size> sz=<file size> nf=<no of files>
            run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/smallFiles pathname="+i.split()[2]+" sz=1K bs=1K nf=1000000 </dev/null>/dev/null 2>&1 &\""
            print run
            os.system(run)
            #Usage: ./lotSmall pathname=<name of the dir> bs=<block size> sz=<file size> nf=<no of files>
            run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/lotSmall pathname="+i.split()[2]+" sz=1K bs=1K nf=1000000 </dev/null>/dev/null 2>&1 &\""
            print run
            os.system(run)
            run = "ssh "+init+" -l nutanix \"sudo cp -rf /home/nutanix/dst.1597252208 "+i.split()[2]+"/testBigFile"+str(l)+"\""
            print run
            os.system(run)
            #Usage: ./createLargeF srcpath=<src file> dstpath=<dst file> bs=<block size> dfs=<destination filesize> rd=<random copy> 
            run = "ssh "+init+" -l nutanix \"sudo /home/nutanix/clSc/createLargeF srcpath="+i.split()[2]+"/testBigFile"+str(l)+" dstpath="+i.split()[2]+" bs=1M dfs="+fsize+" rd=0 </dev/null>/dev/null 2>&1 &\""
            print run
            os.system(run)
            l +=1 
            
   
def sshCopyid(ip,user):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    try :
        cmd = "ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o \"StrictHostKeyChecking no\" "+user+"@"+str(ip)
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
    nodisk = 6
    fsize = '2.4T'
    dsize = '1000G'
    wait = 3600
    onlyS = 0
    userid = 'nutanix'
    image='vgcS'
    cvm = ''
    init=''
    dest=''
    vgm=''
    pat='VG'
    runCnt = 0

    try:
        opts, args = getopt.getopt(argv,"hc:g:i:l:f:d:r:p:w:",["cvm","vgm","init=","dest=","fsize=","dsize=","onlyS=","pat=","wait="])
    except getopt.GetoptError:
        print 'vgSetup.py -c <cvm> -g <vol grp> -i <client> -l <dest cluster > -f <file system size> -d <dsize> -r <run only stress> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'vgSetup.py -c <cvm> -i <client> -l <dest cluster> -f <file system size> -d <dsize> -r <run only stress> -w <wait>'
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-g", "--vgm"):
            vgm = arg
        elif opt in ("-i", "--init"):
            init = arg
        elif opt in ("-l", "--dest"):
            dest = arg
        elif opt in ("-f", "--fsize"):
            fsize = arg
        elif opt in ("-d", "--dsize"):
            dsize = arg
        elif opt in ("-r", "--onlyS"):
            onlyS = int(arg)
        elif opt in ("-p", "--pat"):
            pat = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(init,userid)

    if dest:
        print "Create Clinet and attach "
        (iqn,init,vm) = cofigClient(dest,cvm,pat,vgm,image)

    if cvm:
        ncli = "ssh "+cvm+" -l nutanix /home/nutanix/prism/cli/ncli "
        sshCopyid(cvm,userid)
        discoverLun(ncli,init)

    if not onlyS:
        cmd="scp -r ~/scripts/clSc/ nutanix@"+init+":/home/nutanix/"
        print cmd
        os.system(cmd)
    else :
        cmd = "scp -r /home/santoshkumar.ladi/dst.1597252208 nutanix@"+init+":/home/nutanix/"
        print cmd
        os.system(cmd)

    while 1:
        if not onlyS and runCnt == 0:
            cleanCong(init,dsize)
            configVg(init,fsize,dsize)
        else :
            onlyStress(init,fsize)
        runCnt=runCnt+1
        time.sleep(wait)

if __name__ == "__main__":
    main(sys.argv[1:])


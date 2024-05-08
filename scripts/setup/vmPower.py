#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect

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

    while 1:
        runS(ssh,cvm,patr)

def runS(ssh,cvm,patr):
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "
    userid = 'nutanix'
    ip = ''
    run = ssh+acli +" vm.list power_state=off | grep  \""+patr+"\" | grep -v \"VM name\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(len(output)-1):
        if output[i]:
            (vm,uuid) = output[i].split()
            """
            run = ssh +ncli+" vm list name="+vm+" | grep \"VM IP Addresses\""
            print run
            match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
            if match is not None:
                ip = match.group()
            run = "ssh "+ip+" -l nutanix \"ps -eaf | grep remv\""
            print run
            os.system(run)
            run = "ssh "+ip+" -l nutanix \"sudo chmod 777 /mnt/dataMnt/sdc\""
            print run
            os.system(run)
            run = "ssh "+ip+" -l nutanix \" rm -rf /home/nutanix/scripts ; sudo rm -rf /home/nutanix/data/cores/* \""
            run = "scp -r /home/santoshkumar.ladi/scripts/automation/remv nutanix@"+ip+":/mnt/dataMnt/sdc"
            print run
            os.system(run)
            run = "ssh "+ip+" -l "+userid+" \"sudo /mnt/dataMnt/sdc/remv /mnt/dataMnt/  </dev/null>/dev/null 2>&1 &\""
            print run
            os.system(run)
            run = "ssh "+ip+" -l "+userid+" \"for i in {1..9};do for j in {1..9}; do echo \"sudo rm -rf /mnt/dataMnt/FILE_\$i\$j*\";\`sudo rm -rf /mnt/dataMnt/FILE_\$i\$j*\`;done done </dev/null>/dev/null 2>&1 \""
            print run
            os.system(run)
            run = "ssh "+ip+" -l nutanix \"sudo rm -rf /mnt/dataMnt/FILE* \""
            print run
            os.system(run)
            run = "ssh "+ip+" -l "+userid+" \"sudo kill \$(ps aux | grep 'dataMnt' | grep -v grep | awk '{print \$2}') \""
            print run
            os.system(run)
            run = "ssh "+ip+" -l "+userid+" \"sudo umount -f \$(mount | grep 'dataMnt' | awk '{print \$1}') \""
            print run
            run = "ssh "+ip+" -l nutanix \"sudo rm -rf /mnt/dataMnt/* \""
            print run
            os.system(run)
            os.system(run)
            run = "ssh "+ip+" -l nutanix \"df -kh .\""
            print run
            os.system(run)
            run = "ssh "+ip+" -l nutanix \"df -kh \""
            print run
            os.system(run)
            run = ssh +acli+" vm.nic_create "+vm+" network=vlan0"
            print run
            os.system(run)
            """
            #run = ssh +acli+" vm.delete "+vm
            #print run
            #os.system(run)
            #run = ssh +acli+" vm.off "+vm
            #print run
            #os.system(run)
            #run = ssh +acli+" vm.update "+vm+" memory=2G num_vcpus=2 num_cores_per_vcpu=1" 
            #print run
            #os.system(run)
            #run = ssh +acli+" vm.on "+vm
            #print run
            #os.system(run)

if __name__ == "__main__":
    main(sys.argv[1:])


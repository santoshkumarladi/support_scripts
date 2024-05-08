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
        os.system(cmd)
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


    runS(ssh,cvm,patr)

def runS(ssh,cvm,patr):
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "
    userid = 'nutanix'
    run = ssh+acli +" vm.list | grep \""+patr+"\" | grep -v \"VM name\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(len(output)-1):
        if output[i]:
            (vm,uuid) = output[i].split()
            run = ssh +ncli+" vm list name="+vm+" | grep \"VM IP Addresses\""
            print run
            match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
            if match is not None:
                ip = match.group()
                print vm+" "+uuid+" "+ip
                sshCopyid(ip)
                cmd = "scp -r /home/santoshkumar.ladi/scripts nutanix@"+ip+":/home/nutanix"
                print cmd
                os.system(cmd)
                cmd = "ssh "+ip+" -l nutanix \"sudo kill $(ps aux | grep 'fio'|grep -v grep | awk '{print $2}')\""
                print cmd
                os.system(cmd)
                #cmd = "ssh "+ip+" -l "+userid+" \'sudo python /home/nutanix/scripts/fioWokload/FioWorkload.py </dev/null>/dev/null 2>&1 & \'"
                cmd = "ssh "+ip+" -l "+userid+" \'sudo python /home/nutanix/scripts/fioWokload/FioWorkloadBig.py </dev/null>/dev/null 2>&1 & \'"
                print cmd
                os.system(cmd)


if __name__ == "__main__":
    main(sys.argv[1:])


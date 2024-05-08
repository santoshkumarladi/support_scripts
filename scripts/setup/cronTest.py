#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import threading
import pexpect

outlock = threading.Lock()


def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    cvm = ''
    wait=7200

    try:
        opts, args = getopt.getopt(argv,"hi:w:",["cvm=","wait="])
    except getopt.GetoptError:
        print 'ERROR : testRun.py -i <cvm> -w <wait> '
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'USAGE : testRun.py -i <cvm> -w <wait> '
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvm = arg
        elif opt in ("-w", "--wait"):
            wait  = int(arg)

    sshCopyid(cvm)
    while 1:
        print "Wait -> "+str(wait)
        runS(cvm,mntp,userid,passwd,b,d,ioint,pat)
        time.sleep(wait)

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
        os.system(cmd)

def runTheScript(ip,uuid,mntp,userid,passwd,b,d,ioint):
    #sudo runTest.py -v <vname> -b <breadth> -d<depth> -c<con> -m <mntp> -n <nodrive> -s <disk size>
    #echo '@reboot ( sleep 90 ; sudo /home/nutanix/scripts/setup/stressRun.py -m /mnt/dataMnt -b 4 -d 4 -i 1 )' | /usr/bin/crontab
    if ioint :
        run = "ssh "+ip+" -l "+userid+" \"echo \'@reboot ( sleep 90 ; sudo /home/nutanix/scripts/setup/stressRun.py -m /mnt/dataMnt -b 4 -d 4 -i 1 )\' | /usr/bin/crontab\" "
        print run
        os.system(run)
    else :
        run = "ssh "+ip+" -l "+userid+" \"echo \'@reboot ( sleep 90 ; sudo /home/nutanix/scripts/setup/stressRun.py -m /mnt/dataMnt -b 4 -d 4 -i 0 )\' | /usr/bin/crontab\" "
        print run
        os.system(run)

    run = "ssh "+ip+" -l "+userid+" \"sudo /home/nutanix/scripts/setup/stressRun.py -m " +mntp+ " -b "+str(b)+" -d "+str(d)+" -i "+str(ioint)+" </dev/null>/dev/null 2>&1 &\""
    print run
    os.system(run)


def runS(cvm,mntp,userid,passwd,b,d,ioint,pat):
    vmlist = []
    wait = 10

    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y "
    ncli = " /home/nutanix/prism/cli/ncli "


    run = ssh +acli+" vm.list power_state=on | grep \""+pat+"\" | grep -v \"gold\" | grep -v \"windows\" | grep -v \"VM name\" "
    print run
    output = (os.popen(run).read()).split('\n')
    print output
    random.shuffle(output)
    for i in range(len(output)-1):
        if output[i]:
            (vm,uuid) = output[i].split()
            run = ssh +ncli+" vm list name="+vm+" | grep \"VM IP Addresses\""
            print run
            match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
            if match is not None:
                ip = match.group()
                print vm+" "+uuid+" "+ip
                vmlist.append({'uuid':uuid,'vm':vm,'ip':ip})
                sshCopyid(ip)
                cmd = "ssh "+ip+" -l nutanix \" rm -rf /home/nutanix/scripts ; sudo rm -rf /home/nutanix/data/cores/* \""
                print cmd
                os.system(cmd)
                cmd = "scp -r /home/santoshkumar.ladi/scripts nutanix@"+ip+":/home/nutanix"
                print cmd
                os.system(cmd)
                cmd = "ssh "+ip+" -l nutanix \"/home/nutanix/scripts/setup/killScript.py dataMnt \""
                print cmd
                os.system(cmd)
                runTheScript(ip,uuid,mntp,userid,passwd,b,d,ioint)
 

if __name__ == "__main__":
    main(sys.argv[1:])


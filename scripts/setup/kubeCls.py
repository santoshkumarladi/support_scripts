#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect


def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    cuserid = 'root'
    cpasswd = 'nutanix/4u'
    cvm = ''
    wait=7200
    pat = 'long'

    try:
        opts, args = getopt.getopt(argv,"hi:p:w:",["cvm=","pat=","wait="])
    except getopt.GetoptError:
        print 'ERROR : testRun.py -i <cvm> -p <pattern>  -w <wait> '
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'USAGE : testRun.py -i <cvm> -p <pattern>  -w <wait> '
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--pat"):
            pat  = arg
        elif opt in ("-w", "--wait"):
            wait  = int(arg)

    sshCopyid(cvm,userid)
    vmlist = runS(cvm,userid,passwd,cuserid,pat)

def sshCopyid(ip,userid):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    try :
        cmd = "ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o \"StrictHostKeyChecking no\" "+userid+"@"+str(ip)
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


def runS(cvm,userid,passwd,cuserid,pat):
    vmlist = []

    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y "
    ncli = " /home/nutanix/prism/cli/ncli "


    run = ssh +acli+" vm.list | grep \""+pat+"\" | grep -v \"gold\" | grep -v \"windows\" | grep -v \"VM name\" "
    print run
    output = (os.popen(run).read()).split('\n')
    print output
    random.shuffle(output)
    for i in range(len(output)-1):
        if output[i]:
            (vm,uuid) = output[i].split()
            run = ssh +acli+" vm.on "+vm
            os.system(run)
            time.sleep(20)
            run = ssh +ncli+" vm list name="+vm+" | grep \"VM IP Addresses\""
            print run
            match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
            if match is not None:
                ip = match.group()
                print vm+" "+uuid+" "+ip
                vmlist.append({'uuid':uuid,'vm':vm,'ip':ip})
                sshCopyid(ip,cuserid)
    return vmlist 

if __name__ == "__main__":
    main(sys.argv[1:])


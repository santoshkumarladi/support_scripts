#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect


def node_unconfigure(svmip):
    ssh = "ssh "+svmip+" -l nutanix"
    run = ssh +" sudo sed -i '/zk/d' /etc/hosts "
    print run
    os.system(run)
    run = ssh +" touch .node_unconfigure "
    print run
    os.system(run)
    run = ssh +" \" source /etc/profile; /usr/local/nutanix/cluster/bin/genesis restart \""
    print run
    os.system(run)
    time.sleep(60)
    run = ssh +" sudo reboot " 
    print run
    os.system(run)

def restart_genesis(svmip):
    ssh = "ssh "+svmip+" -l nutanix"
    run = ssh +" \" source /etc/profile; /usr/local/nutanix/cluster/bin/genesis restart ; sudo reboot \""
    print run
    os.system(run)

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

def main(argv):
    cmd = ''
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    wait=0
    unconfig=0

    try:
        opts, args = getopt.getopt(argv,"hc:u:w:",["cvm=","unconfig=","wait="])
    except getopt.GetoptError:
        print 'clusterDest.py -c <cvm> -u <destroy> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'clusterDest.py -c <cvm> -u <destroy> -w <wait> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-u", "--unconfig"):
            unconfig = int(arg)
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    svmips =  cvm.split(",")
    for  svmip in svmips:
        print svmip
        sshCopyid(svmip,userid)
        restart_genesis(svmip)
        if unconfig: 
            node_unconfigure(svmip)
        time.sleep(wait)

if __name__ == "__main__":
    main(sys.argv[1:])


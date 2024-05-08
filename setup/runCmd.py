#!/usr/bin/python

import sys, getopt,os,re
import pexpect
import string
import time

def sshCopyid(ip,userid,passwd):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    #passwd="nutanix/4u"
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
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    cmd = ''
    wait = 30
    try:
        opts, args = getopt.getopt(argv,"hi::c:p:w:",["cvm=","cmd=","passwd=","wait="])
    except getopt.GetoptError:
        print 'runTest.py -i <cvm> -c <cmd> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'runTest.py -i <cvm> -c <cmd> -w <wait>'
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvmList = arg
        elif opt in ("-c", "--con"):
            cmd = arg
        elif opt in ("-p", "--passwd"):
            passwd = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)


    svmips =  cvmList.split(",")
    for  svmip in svmips:
        print svmip
        sshCopyid(svmip,userid,passwd)
    while 1:
        for  svmip in svmips:
            ssh = "ssh "+svmip+" -l "+userid
            runTheCMd(ssh,cmd)  
        time.sleep(wait)

def runTheCMd(ssh,cmd):
    run = ssh+" \' for ip in `/usr/local/nutanix/cluster/bin/svmips`; do echo $ip;  ssh -q $ip \'"+cmd+"\' ;done \' "
    print run
    os.system(run)

if __name__ == "__main__":
    main(sys.argv[1:])


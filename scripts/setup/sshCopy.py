#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect

def sshCopyi(ip):
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

def get_svmips(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh -o ConnectTimeout=10 "+cvm+" -l nutanix"
    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    if op :
        output = op.split('\n')
        for i in range(1,len(output)):
            print output[i].split()[4]
            #if output[i].split()[4] != 'False':
            if output[i].split()[4]:
                svmips.append(output[i].split()[-1])
                #print output[i].split()[-1]
        return svmips


def sshCopyid(ip,passwd):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    #passwd="nutanix/4u"
    rsa_key = '\(yes\/no\)\?'
    prompt = "assword:"
    non_rsa='you wanted were added.'

    #cmd = "ssh-keygen -R "+str(ip)
    #os.system(cmd)
    cmd = " /usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@"+str(ip)
    print cmd
    child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@%s'%(ip))
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
     passwd = 'RDMCluster.123'
     cmd = ''
     try:
         opts, args = getopt.getopt(argv,"h:p:c:",["cvm=","passwd="])
     except getopt.GetoptError:
         print 'cvmSnapshot.py -c <cvm> '
         sys.exit(2)
     for opt, arg in opts:
         if opt == '-h':
             print 'cvmSnapshot.py -c <cvm> '
             sys.exit()
         elif opt in ("-c", "--cvm"):
             cvm = arg
         elif opt in ("-p", "--passwd"):
             passwd = arg

     sshCopyid(cvm,passwd)
     svmips = get_svmips(cvm)
     for  svmip in svmips:
         sshCopyid(svmip,passwd)

     ssh = "ssh "+cvm+" -l "+userid

     acli = " /usr/local/nutanix/bin/acli -y"
     ncli = " /home/nutanix/prism/cli/ncli "
     run = ssh+" ls -lrt"
     print run
     os.system(run)

     run = ssh +acli+" vm.list | grep -v \"uptime\""
     print run
     output = (os.popen(run).read()).split('\n')
     for i in range(2,len(output)-1):
         #VM name  VM UUID
         #vm1      f347f020-5b42-481f-a2a4-74aad770a333
         (vm,uuid) = output[i].split()
         run = ssh +ncli+" vm list name="+vm+" | grep \"VM IP Addresses\""
         print run
         #    VM IP Addresses           : 10.46.141.186
         match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
         if match is not None:
             ip = match.group()
             print vm+" "+uuid+" "+ip
             sshCopyid(ip)

if __name__ == "__main__":
    main(sys.argv[1:])


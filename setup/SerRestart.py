#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import itertools

def sshCopyid(ip):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    cmd = "ssh-keygen -R "+str(ip)
    os.system(cmd)
    try :
        cmd = " /usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@"+str(ip)
        print cmd
        child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@%s'%(ip))
        r=child.expect ('you wanted were added.')
        print "Outp"+str(r)
        if r==1:
            cmd = " ssh "+str(ip)+" nutanix -l pwd"
            print cmd
            child = pexpect.spawn('ssh %s nutanix -l pwd'%(ip))
            rsa_key = '\(yes\/no\)\?'
            prompt = "Password:"
            i = child.expect([rsa_key,prompt,""])
            if i==0:
                child.sendline('yes')
                child.expect(prompt)
                child.sendline(passwd)
            elif i==1:
                child.sendline(passwd)
            else:
                child.sendline(passwd)
        child.interact()
        child.close()
    except Exception as e:
        print "Oops Something went wrong buddy"
        #print e

def get_svmips(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    #print "Op ---> "+op
    if op :
        output = op.split('\n')
        for i in range(1,len(output)):
            if output[i].split()[3] == 'AcropolisNormal':
                svmips.append(output[i].split()[-1])

        return svmips


def killService(svmip,service,svmips):
    ssh = "ssh "+svmip+" -l nutanix "
    cmd = ssh+" \"source /etc/profile; /usr/local/nutanix/cluster/bin/genesis stop "+service +"\""
    print cmd 
    os.system(cmd)
    time.sleep(1200)
    ssh = "ssh "+svmips[random.randint(0,len(svmips)-1)]+" -l nutanix "
    cmd = ssh+"\"/usr/local/nutanix/cluster/bin/cluster status </dev/null>/dev/null 2>&1\""
    print cmd 
    os.system(cmd)
    cmd = ssh+"\"source /etc/profile; /usr/local/nutanix/cluster/bin/genesis restart \""
    print cmd 
    os.system(cmd)
    ssh = "ssh "+svmips[random.randint(0,len(svmips)-1)]+" -l nutanix "
    cmd = ssh+"\"/usr/local/nutanix/cluster/bin/cluster start </dev/null>/dev/null 2>&1\""
    print cmd 
    os.system(cmd)

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    wait = 6600
    services=""
    #services = "stargate,zookeeper,curator,xmount,anduril,pithos"
    try:
        opts, args = getopt.getopt(argv,"hc:w:s:p:",["cvm=","wait=","services=","passwd="])
    except getopt.GetoptError:
        print 'SerRestart.py -c <cvm> -s <services> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'SerRestart.py -c <cvm> -s <services> -w <wait>'
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-s", "--services"):
            services = arg
        elif opt in ("-p", "--password"):
            passwd = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    services = services.split(',')
    print services
    sshCopyid(cvm)
    #services = ["stargate","zeus","cassandra","curator","xmount"]
    #services = ["stargate","zookeeper","curator","xmount","pithos","cassandra"]
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    run = ssh+" /usr/local/nutanix/cluster/bin/ipmiips"
    print run
    output = (os.popen(run).read()).split('\n')
    ipmips = output[0].split()
    print ipmips
 
    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    for  svmip in svmips:
        sshCopyid(svmip)
    while 1:
        random.shuffle(svmips)
        runS(cvm,svmips,services,wait)
        #for svmip in svmips:
        #    cmd = "ssh "+svmip+" -l "+userid+" \" sudo mkdir /mnt/archive;sudo mount 10.40.231.197:/volume1 /mnt/archive \""
        #    print cmd 
        #    os.system(cmd)


def runS(cvm,svmips,services,wait):
    count = 1
    i=0
    while count <= 2:
        print "count -->"+str(count)
        svmips = get_svmips(svmips[random.randint(0,len(svmips)-1)])
        #for (svmip,service) in itertools.izip(svmips,services):
        for svmip in svmips:
            print svmip
            killService(svmip,services[i],svmips)
            if i < len(services)-1:
                i = i+1
            else :
                i = 0
            time.sleep(wait)
        count=count+1

if __name__ == "__main__":
    main(sys.argv[1:])


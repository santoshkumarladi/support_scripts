#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import json
import pexpect
import itertools

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

def get_svmip(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    print "Op ---> "+op
    if op :
        output = op.split('\n')
        for i in range(1,len(output)):
            if output[i].split()[4] != 'False':
                svmips.append(output[i].split()[-1])

        return svmips

def get_svmips(cvm):
    svmips = []
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    return svmips

def get_clu(cvm):

    userid = 'nutanix'
    passwd = 'nutanix/4u'
    ssh = "ssh "+cvm+" -l "+userid
    ncli = " /home/nutanix/prism/cli/ncli "
    cmd = ssh+ncli+" -json=true host list"
    print cmd
    op = os.popen(cmd).read()
    p_dict = json.loads(op)
    print(json.dumps(p_dict, indent = 4, sort_keys=True))

def killService(svmip,service,svmips):
    ssh = "ssh "+svmip+" -l nutanix "
    cmd = ssh+"pkill "+service
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

    try:
        opts, args = getopt.getopt(argv,"hc:w:",["cvm=","wait="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm)
    services = ["stargate","zeus","cassandra","curator","xmount"]
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


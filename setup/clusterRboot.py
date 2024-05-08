#!/usr/bin/python

import sys, getopt,os,re
import pandas as pd
import random
import string
import time
import datetime
import pexpect
import itertools

def sshCopyid(ip,passwd):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    #passwd="nutanix/4u"
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

def killService(svmip,service,wait):
    ssh = "ssh "+svmip+" -l nutanix "
    #cmd = ssh+"pkill "+service
    cmd = ssh+"/usr/local/nutanix/cluster/bin/genesis stop "+service
    print cmd 
    os.system(cmd)
    time.sleep(wait)
    cmd = ssh+"\"/usr/local/nutanix/cluster/bin/cluster status </dev/null>/dev/null 2>&1\""
    print cmd 
    os.system(cmd)
    cmd = ssh+"\"/usr/local/nutanix/cluster/bin/cluster start </dev/null>/dev/null 2>&1\""
    print cmd 
    os.system(cmd)

def check_failnode(cvm):
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"

    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    print "Op ---> "+op
    if op :
        output = op.split('\n')
        for i in range(1,len(output)-1):
            if output[i].split()[4] == 'True':
                print output[i].split()[7]
                return output[i].split()[7]

    else :
        print "return the down cvm -- > "+cvm
        return cvm


def get_crator_master(cvm,userid,svmips):
    cu_m = 'none'
    for  svmip in svmips:
        try :
            url =r'http://'+svmip+':2010'
            print url
            tables = pd.read_html(url,match='Master')
            op = tables[1].values.tolist()
            for r in op:
                if 'Master' in r:
                    print "Curator Master --> "+r[1]
                    cu_m = r[1]
        except :
            print "Error in get_crator_master or Not master"
    if cu_m == 'none' :
        print "Not able to find curator master "
        time.sleep(30)
    else :
        return cu_m

def get_curstatus(cvm,userid,svmips):
    curator_master = get_crator_master(cvm,userid,svmips)
    while curator_master == 'none':
        curator_master = get_crator_master(cvm,userid,svmips)

    try :
        url =r'http://'+curator_master
        print url
        tables = pd.read_html(url)
        print tables[3]
        op = tables[3].to_dict()
        print op 
        pct = op['Reasons']['NodeFailure'][3]
        print"--" +pct 
    except :
        print "Error in get_tierusage"
        sys.exit(2)

def get_svmips(cvm):
    #run = "ssh "+cvm+" -l nutanix /usr/local/nutanix/cluster/bin/svmips"
    #print run
    #output = (os.popen(run).read()).split('\n')
    #svmips = output[0].split()
    #return svmips
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
                print output[i].split()[7]
                svmips.append(output[i].split()[7])

        return svmips


def get_hostips(cvm):
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
                svmips.append(output[i].split()[1])

        return svmips


def isDiskFailing(cvm):
    ssh = "ssh "+cvm+" -l nutanix"
    ncli = " /home/nutanix/prism/cli/ncli "
    run = ssh +ncli+"disk get-remove-status | grep \"Host Name\""
    op = os.popen(run).read()
    print "Disk fail --> "+op
    if op :
        op = os.popen(run).read().split(':')
        op = op[1].strip()
        return op
    else :
        return None

def main(argv):
    userid = 'ADMIN'
    passwd = 'ADMIN'
    cvmpas = 'nutanix/4u'
    wait = 28800
    power = 0
    try:
        opts, args = getopt.getopt(argv,"hc:p:u:d:x:w:",["cvm=","power=","userid=","passwd=","cvmpas=","wait="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--power"):
            power = arg
        elif opt in ("-u", "--userid"):
            userid = arg
        elif opt in ("-d", "--passwd"):
            passwd = arg
        elif opt in ("-x", "--cvmpas"):
            cvmpas = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm,cvmpas)
    ssh = "ssh "+cvm+" -l nutanix"
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    run = ssh+" /usr/local/nutanix/cluster/bin/ipmiips"
    print run
    output = (os.popen(run).read()).split('\n')
    ipmips = output[0].split()
    print ipmips
    for ipmip in ipmips:
        runS(ipmip,power,userid,passwd,wait)


def runS(ipmip,op,userid,passwd,wait):
       x = datetime.datetime.now()
       print x
       cmd = "/usr/bin/ipmitool  -H " +ipmip+" -U "+userid+" -P "+passwd+" chassis power "+str(op)
       print cmd
       os.system(cmd)
       time.sleep(wait)
       if op == "off":
           cmd = "/usr/bin/ipmitool  -H " +ipmip+" -U "+userid+" -P "+passwd+" chassis power on"
           #cmd = "/usr/bin/ipmitool  -H " +ipmip+" -U ADMIN -P ADMIN chassis power  on"
           print cmd
           os.system(cmd)
       elif op == "o":
           cmd = "/usr/bin/ipmitool  -H " +ipmip+" -U "+userid+" -P "+passwd+" chassis power off"
           #cmd = "/usr/bin/ipmitool  -H " +ipmip+" -U ADMIN -P ADMIN chassis power  off"
           print cmd
           os.system(cmd)

if __name__ == "__main__":
    main(sys.argv[1:])


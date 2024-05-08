#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import threading
from collections import defaultdict 


def calculate_usage_percentages(data_str):
    # Split the data string into lines
    lines = data_str.strip().split("\n")
    
    # Initialize variables to store memory and CPU usage values
    memory_usage_bytes = 0
    total_memory_bytes = 0
    cpu_usage_percent = 0
 
    # Extract memory and CPU usage values
    for line in lines:
        if "cpu_usage_ppm" in line:
            cpu_usage_percent = int((float(line.split(":")[-1].strip()) / 1000000) * 100)
        elif "mem_usage_bytes" in line:
            memory_usage_bytes = int(line.split(":")[-1].strip())
        elif "memory_size_bytes" in line:
            total_memory_bytes = int(line.split(":")[-1].strip()) 
 
    # Calculate memory usage percentage
    memory_usage_percent = int((float(memory_usage_bytes) / total_memory_bytes) * 100)
    return memory_usage_percent, cpu_usage_percent


def sshCopyid(ip,passwd):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    #passwd="nutanix/4u"
    rsa_key = '\(yes\/no\)\?'
    prompt = "assword:"
    non_rsa='you wanted were added.'
    userid="nutanix"

    cmd = "ssh-keygen -R "+str(ip)
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

def getHostVmList(cvm):
    usage = {}
    hostvm = defaultdict(list)
    ssh = "ssh "+cvm+" -l nutanix "
    acli = " /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    run = "ssh "+cvm+" -l nutanix /usr/local/nutanix/cluster/bin/hostips"
    output = (os.popen(run).read()).split('\n')
    hostips = output[0].split()
    print hostips
    
    for host in hostips:
        try :
            cmd = ssh+" ssh root@"+host+" virsh list | grep CVM"
            print cmd
            cvm = (os.popen(cmd).read()).split()[1]
            if 'CVM' in cvm :
                cmd = ssh+acli+" host.list_vms "+host+" | grep -v vgclient | grep -v ltss | grep -v auto "
                print cmd
                op = (os.popen(cmd).read()).split('\n')
                hostvm[cvm] = []
                for i in range(1,len(op)-1):
                     hostvm[cvm].append(op[i].split()[0])
                     print op[i].split()[0] 
                
                cmd = ssh+acli+" host.get "+host
                print cmd
                op = (os.popen(cmd).read())
                (mem,cpu) = calculate_usage_percentages(op)
                print "host {} memory usage % {} and cpu % {}".format(host,mem,cpu)
                usage[cvm] = {"mem":mem,"cpu":cpu}
        except:
            print "Failed to get the CVM usage"
    return hostvm,usage

def checkCvmCpuUse(svm,hvm,hostvms,cpu,cpuP,memP):
    ssh = "ssh -o ConnectTimeout=10 "+svm+" -l nutanix "
    acli = " /usr/local/nutanix/bin/acli -y"
    print " <---- Host name -> {}, cpu -> {} , mem usage is -> {} and cpu threshold -> {} ----> ".format(hvm,cpuP,memP,cpu)
    if cpuP > cpu or memP > cpu:
        for vm in hostvms:
            run = ssh+acli+" vm.off "+vm
            print run 
            os.system(run)
    else :
        for vm in hostvms:
            run = ssh+acli+" vm.on "+vm
            print run
            os.system(run)
        if not hostvms:
            time.sleep(20)
      
def vmPwer(cvm):
    acli = " /usr/local/nutanix/bin/acli -y"
    ssh = "ssh -o ConnectTimeout=10 "+cvm+" -l nutanix"
    userid = 'nutanix'
    ip = ''
    run = ssh+acli +" vm.list | grep -v auto |  grep -v ltss | grep -v \"VM name\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(len(output)-1):
        if output[i]:
            (vm,uuid) = output[i].split()
            run = ssh +acli+" vm.on "+vm
            print run
            os.system(run)
 
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
            if output[i].split()[3] == 'AcropolisNormal':
            #if output[i].split()[4]:
                svmips.append(output[i].split()[-1])
                print output[i].split()[-1]
        return svmips

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    cpu = 70
    wait = 1200

    try:
        opts, args = getopt.getopt(argv,"hc:p:w:u:",["cvm=","cpu=","wait=","passwd="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -p <cpu> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -p <cpu> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--cpu"):
            cpu = int(arg)
        elif opt in ("-u", "--passwd"):
            passwd = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm,passwd)
    svmips = get_svmips(cvm)
    for  svmip in svmips:
        sshCopyid(svmip,passwd)

    runS(cvm,userid,passwd,cpu,wait)


def runS(cvm,userid,passwd,cput,wait):
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh -o ConnectTimeout=10 "+cvm+" -l nutanix"
    
    print "Wait ---> "+str(wait)
    while 1:    
        threads = []
        hostvm = {}
        usage = {}
        try :
            svmips = get_svmips(cvm)
            print svmips
            svm = svmips[random.randint(0,len(svmips)-1)]
            hostvm,usage = getHostVmList(svm)
    
            for cvmn in hostvm.keys():    
                svm = svmips[random.randint(0,len(svmips)-1)]
                print "Hostname -> {} memory usage % {} and cpu % {}".format(cvmn,usage[cvmn]["mem"],usage[cvmn]["cpu"])
                t = threading.Thread(target=checkCvmCpuUse, args=(svm,cvmn,hostvm[cvmn],cput,usage[cvmn]["cpu"],usage[cvmn]["mem"],))
                threads.append(t)

            for x in threads: 
                x.start()

            for x in threads: 
                x.join()

        except Exception as e:
            print "Oops Something went wrong buddy + wait and restart "
            print e
            #run = ssh+" \""+acli+"vm.off \* \" &"
            #print run 
            #os.system(run)
        time.sleep(wait)

if __name__ == "__main__":
    main(sys.argv[1:])


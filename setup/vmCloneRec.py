#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect


def delVmbyPattern(ssh,vname):
    run = ssh +" vm.list"+" | grep \""+vname+"\""
    output = (os.popen(run).read()).split('\n')
    for i in range(1,len(output)-1):
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.delete "+uuid
        print cmd
        os.system(cmd)

def get_svmips(cvm):
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
            if output[i].split()[4] != 'False' and output[i].split()[6] != 'False':
                svmips.append(output[i].split()[-1])

        return svmips

def createNestedCl(ssh,clone_from_vm,count,total,vms):
    for i in range(count):
        clone_name = clone_from_vm+"random"+str(random.randint(100,128908))
        cmd = ssh+ " vm.clone " +clone_name+" clone_from_vm=" + clone_from_vm
        print cmd
        op = os.popen(cmd).read()
        #complete
        match = re.match(r'(.*):\s+complete(.*)', op)
        if match is not None:
            cmd = ssh+ " vm.on " +clone_name
            print cmd
            os.system(cmd)
            clone_from_vm = clone_name
            time.sleep(20)
            if vms <= total:
                break
            else:
                vms = vms+1
                createNestedCl(ssh,clone_from_vm,count,total,vms)
            
        else :
            break

def createNestedClone(ssh,clone_from_vm,count,total,vms):
    for i in range(count):
        clone_name = "cl_r_"+str(random.randint(100,128908))+"_"+str(i)
        cmd = ssh+ " vm.clone " +clone_name+" clone_from_vm=" + clone_from_vm
        print cmd
        op = os.popen(cmd).read()
        #complete
        print op
        match = re.search(r'(.*):\s+complete(.*)', op)
        if match is not None:
            cmd = ssh+ " vm.on " +clone_name
            print cmd
            os.system(cmd)
            clone_from_vm = clone_name
            time.sleep(20)
            if vms >= total:
                break
            else:
                vms = vms+1
                print "clone_from_vm "+str(clone_from_vm)+" vms "+str(vms)
                #createNestedClone(ssh,clone_from_vm,count,total,vms)
            
        else :
            break

def sshCopyid(ip):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    rsa_key = '\(yes\/no\)\?'
    prompt = "assword:"
    non_rsa='you wanted were added.'

    cmd = "ssh-keygen -R "+str(ip)
    os.system(cmd)
    try :
        cmd = " /usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@"+str(ip)
        print cmd
        child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@%s'%(ip))
        #r=child.expect ('you wanted were added.')
        r= child.expect([non_rsa,rsa_key,prompt,"",pexpect.EOF],timeout=30)
        print "Outp"+str(r)
        if r==2:
            child.sendline('yes')
            child.expect(prompt)
            child.sendline(passwd)
        elif r==3:
            child.sendline(passwd)
        else :
            child.expect(prompt)
            child.sendline(passwd)
        child.interact()
        child.close()
    except Exception as e:
        print "Oops Something went wrong buddy"
        print e

def main(argv):
    cmd = ''
    userid = 'nutanix'
    nocl = 2
    novol = 4
    pat = ''
    wait=600
    try:
        opts, args = getopt.getopt(argv,"hc:n:j:p:w:",["cvm=","nocl=","novol=","pat=","wait="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> -n <no of clone> -j <no vol>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> -n <no of clone> -j <no of vols>'
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--pat"):
            pat = arg
        elif opt in ("-n", "--nocl"):
            nocl = int(arg)
        elif opt in ("-j", "--novol"):
            novol = int(arg)
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    sshCopyid(cvm)
    ssh = "ssh "+cvm+" -l "+userid
    acli = " /usr/local/nutanix/bin/acli -y"
    #run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    #output = (os.popen(run).read()).split('\n')
    #svmips = output[0].split()
    svmips  = get_svmips(cvm)
    for  svmip in svmips:
        sshCopyid(svmip)
    #hostplist =  output[0].replace(" ", ",")
    #lst = output[0].split()
    lst = svmips
    total = nocl*novol
    vms = 0
    while 1:
        delVmbyPattern(ssh + acli,"cl_r_")
        #run = ssh +acli+" vm.power_cycle *"
        #print run
        #os.system(cmd)
        #time.sleep(72)
        if pat:
            run = ssh +acli+" vm.list | grep \""+pat+"\" | grep -v \"VM name\" "
        else :
            run = ssh +acli+" vm.list | grep -v \"VM name\" "
        print run
        output = (os.popen(run).read()).split('\n')
        try:
            if len(output) > 2:
                print "------------> "+str(novol)
                #random.shuffle(output)
                for i in range(novol):
                    (vm,uuid) = output[i].split()
                    random.shuffle(lst)
                    cvm = lst[len(lst)-1]
                    print 'Run test on the CVM -> ',cvm
                    ssh = "ssh "+cvm+" -l "+userid
                    createNestedClone(ssh+acli,vm,nocl,total,vms)
            else :
                print "going to sleep "+str(wait)
                time.sleep(wait)
        
        except Exception as e:
            print "Oops Something went wrong buddy"
        time.sleep(wait)

if __name__ == "__main__":
    main(sys.argv[1:])


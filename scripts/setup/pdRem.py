#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import pexpect
import threading

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


def pdDelSnap(run,cvm,acli,start,off,out):
    print "start the delete on range "+str(start) +" off "+str(off)
    i = 0
    while i < off:
        if out[start]:
            (tmp,pd) = out[start].split(":")
            cmd = run +"pd clear-schedules name="+pd.strip()
            print cmd
            os.system(cmd)
            cmd = run + " pd rm-snap name="+pd.strip()+" clear-all=true "
            print cmd 
            os.system(cmd)
            #time.sleep(120)
            #pd list name=testPD_long_run_vm_test29
            cmd = run +" pd list name="+pd.strip()+" | grep \"VM Name\" "
            print cmd
            ops = (os.popen(cmd).read())
            
            #if 'None' not in op :
            if ops :
                try:
                    for op in ops.split('\n'):
                        if op:
                            vm = op.split(":")[1]
                            cmd = run +" pd unprotect name="+pd.strip()+" vm-names="+vm.strip()
                            print cmd
                            os.system(cmd)
                            cmd = run + " pd remove name="+pd.strip()
                            print cmd
                            os.system(cmd)
                            #cmd = acli+ " vm.delete "+vm.strip()
                             #print cmd
                            #os.system(cmd)
                except Exception as e:
                    print ops
            else :
                cmd = run + " pd remove name="+pd.strip()
                print cmd
                os.system(cmd)
                

        i = i+1
        start = start+1

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    pat = 'long'
    try:
        opts, args = getopt.getopt(argv,"hc:p:",["cvm=","pat="])
    except getopt.GetoptError:
        print 'cvmSnapshot.py -c <cvm> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'cvmSnapshot.py -c <cvm> '
            sys.exit()
        elif opt in ("-c", "--cvm"):
            cvm = arg
        elif opt in ("-p", "--pat"):
            pat = arg

    sshCopyid(cvm)



    runS(cvm,pat)

def runS(cvm,pat):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    threads = []

    ssh = "ssh "+cvm+" -l "+userid
    acli = "ssh "+cvm+" -l "+userid+" /usr/local/nutanix/bin/acli -y"
    ncli = " /home/nutanix/prism/cli/ncli "

    run = ssh+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    #for  svmip in svmips:
    #    sshCopyid(svmip)

    start =2

    cmd = ssh +ncli +"pd list | grep \"Protection Domain\" | grep \""+pat+"\""
    print cmd
    out = (os.popen(cmd).read()).split('\n')
    off = len(out)/len(svmips)
    pdDelSnap(ssh+ncli,cvm,acli,start,len(out)-1,out)
    
    for svmip in svmips:
        ssh = "ssh "+svmip+" -l "+userid
        print svmip,start,off
        t = threading.Thread(target=pdDelSnap, args=(ssh+ncli,svmip,acli,start,off,out,))
        start = start+off
        threads.append(t)
        #time.sleep(120)

    for x in threads:
        x.start()

    for x in threads:
        x.join()

if __name__ == "__main__":
    main(sys.argv[1:])


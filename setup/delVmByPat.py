#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time

def delVmbyPattern(ssh,vname):
    run = ssh +" vm.list"+" | grep \""+vname+"\""
    print run
    output = (os.popen(run).read()).split('\n')
    for i in range(1,len(output)-1):
        #VM name  VM UUID
        #vm1      f347f020-5b42-481f-a2a4-74aad770a333
        (vm,uuid) = output[i].split()
        cmd = ssh+" vm.delete "+uuid
        print cmd
        os.system(cmd)
def main():
    cvm = sys.argv[1]
    ssh = "ssh "+cvm+" -l nutanix"
    acli = " /usr/local/nutanix/bin/acli -y" 
    delVmbyPattern(ssh+acli,sys.argv[2])

if __name__ == "__main__":
    main()

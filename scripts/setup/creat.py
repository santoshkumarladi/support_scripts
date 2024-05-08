#!/usr/bin/python
import sys, getopt,os,re

def get_op():
    cmd = []
    run = " cat diskL | grep Id "
    op = os.popen(run).read().split('\n')
    for l in op:
        if l:
            d = "".join(l.split(' ')[-1])
            cmd.append(d)
    p = "/home/nutanix/prism/cli/ncli storagepool create disk-ids=\""+ ','.join(cmd)+"\" name=\"default\""
    print p
    os.system(p)

if __name__ == "__main__":
    get_op()

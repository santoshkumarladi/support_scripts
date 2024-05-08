#!/usr/bin/python

import sys,os
import string
import time

def killS(patr):
    cmd = "sudo kill $(ps aux | grep '"+patr+"' | grep -v grep | grep -v killScript.py | awk '{print $2}')"
    print cmd
    os.system(cmd)
    #cmd = "sudo umount -f $(mount | grep '"+patr+"' | grep -v grep | awk '{print $1}')"
    #print cmd
    #os.system(cmd)
    #cmd = "sudo rm -rf /mnt/"+patr+"/*"
    #print cmd
    #os.system(cmd)

def main():
        
    killS(sys.argv[1])

if __name__ == "__main__":
    main()

#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import subprocess

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    logpath="/home/nutanix/log_fio"
    path="/home/nutanix/stressFio.py"
    file_size="2G"

    try:
        opts, args = getopt.getopt(argv,"hp:l:s:",["path=","logpath=","filesize="])
    except getopt.GetoptError:
        print 'stressFio.py -p <path> -l <logpath> -s <files_size> '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'stressFio.py -p <path> -l <logpath> -s <files_size> '
            sys.exit()
        elif opt in ("-p", "--path"):
            path = arg
        elif opt in ("-l", "--logpath"):
            logpath = arg
        elif opt in ("-s", "--filesize"):
            file_size = arg

    vmAddDisk(path,logpath,filesize)


def vmAddDisk(path,logpath,filesize):
    cmd = "/usr/bin/lsblk -S -f -s | grep -v rom"
    output = (os.popen(cmd).read()).split('\n')
    for i in range(2,len(output)-1):
        if 'ext4' not in output[i] :
            line = output[i].split() 
            print "scsci device -> "+line[0]
            if line[0]:
                runTheScript(line,path,logpath,filesize)
 
def runTheScript(lun,path,logpath,filesize):
    mntp = "/dev/"+lun
    
    run = "sudo "+path+" "+mntp+" "+logpath+" "+filesize+ " </dev/null>/dev/null 2>&1 &"
    print run
    os.system(run)
    
if __name__ == "__main__":
    main(sys.argv[1:])


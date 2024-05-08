#!/usr/bin/python

import sys, getopt,os,re
import random
import string
import time
import subprocess

def main(argv):
    wait=7200
    path=''
    try:
        opts, args = getopt.getopt(argv,"hs:w:",["filesize=","wait="])
    except getopt.GetoptError:
        print 'stressFio.py -s <files_size> -w <wait>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'stressFio.py -s <files_size> -w <wait>'
            sys.exit()
        elif opt in ("-s", "--filesize"):
            file_size = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)

    kcmd = "sudo kill -9 $(ps aux | grep 'fio' | grep -v fio_s | awk '{print $2}')"
    cmd="find /home/nutanix/fio_s -type f -name \"fio*.sh\" -print"
    #cmd="find /home/santoshkumar.ladi/scripts/setup/fio_s -type f -name \"fio*.sh\" -print"
    scripts = os.popen(cmd).read().split('\n')
    i=0
    while True:
        #os.system(kcmd)
        #os.system("sudo rm -rf /home/nutanix/*.received")
        #os.system("sudo rm -rf /home/nutanix/*.expected")

        if "fio_seq_write.sh" in scripts[i] :
            path = scripts[i]+" 8 2000000 64 1M 3600 --time_based "
        elif "fio_rand_write_intelerad_burst.sh" in scripts[i] :
            path = scripts[i]+" 8 "
        elif "fio_rand_read.sh" in scripts[i] :
            path = scripts[i]+" 8 3600 128 64K"
        elif "fio_seq_mixed.sh" in scripts[i] :
            path = scripts[i]+" 8 3600 64 128K 50 50 "
        elif "fio_rand_write.sh" in scripts[i] :
            path = scripts[i]+" 8 3600 64 256K --time_based"
        elif "fio_rand_stress.sh" in scripts[i] :
            path = scripts[i]+" 8 2000000 128 512K 3600 20 8"
        elif "fio_rand_mixed.sh" in scripts[i] :
            path = scripts[i]+" 8 3600 128 512K 80 20 --time_based"
        elif "fio_seq_stress.sh" in scripts[i] :
            path = scripts[i]+" 8 2000000 32 1M 3600 50 7 "
        elif "fio_seq_read.sh" in scripts[i] :
            path = scripts[i]+" 8 2000000 64 1M 3600 --time_based "
        elif "fio_seq_fidelity.sh" in scripts[i] :
            path = scripts[i]+" 8 2000000 64 320K 3600 50 "
        elif "fio_rand_write_intelerad_sustained.sh" in scripts[i] :
            path = scripts[i]+" 8 "
        elif "fio_rand_fidelity.sh" in scripts[i] :
            path = scripts[i]+" 8 2000000 128 512K 3600 20 "
        elif "fio_cache_seq_read.sh" in scripts[i] :
            path = scripts[i]+" 8 64 64K 2000000"
        elif "fio_cache_rand_read.sh" in scripts[i] :
            path = scripts[i]+" 8 64 1M 2000000"
        elif "fio_low_qd_rand_write.sh" in scripts[i] :
            path = scripts[i]+" 8 32 3600 1M 2000000"

        run = "sudo sh "+path
        print run
        os.system(run)
        #runTheScript(path)
        i = i+1 if i < len(scripts)-1  else 0
        time.sleep(wait)

def runTheScript(path,filesize,ioen):
    
    run = "sudo sh "+path
    print run
    os.system(run)
    
if __name__ == "__main__":
    main(sys.argv[1:])


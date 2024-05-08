#!/usr/bin/python

from __future__ import division
import sys, getopt,os,re
import pandas as pd
import random
import string
import time
import itertools
import pexpect
import lxml
import threading
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta


def get_svmips(cvm):
    svmips = []
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"
    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    #print "Op ---> "+op
    if op :
        output = op.split('\n')
        for i in range(1,len(output)):
            if output[i].split()[3] == 'AcropolisNormal':
                svmips.append(output[i].split()[-1])

        return svmips


def get_tier_link(cvm, userid, tier, curator_master, svmips):
    url =r'http://'+curator_master+'/master/tierusage'
    tables = pd.read_html(url)
    print tables[1]
    op = tables[1].to_dict()
    pct = op['Tier Usage Pct'][tier][:-1]
    print op['Tier Usage Pct'][tier]
    print "Current Tier usage is ->> "+str(pct)


def parse_output_and_get_total_ssd_usage(output):
    # Split the output into lines and filter SSD lines (exclude rows with N/A)
    
    input_list = [line for line in output.strip().split('\n') if "SSD" in line and "N/A" not in line]
    result_list = [line.split("|") for line in input_list]
    result_list = [[item for item in line_split if item] for line_split in result_list]
    last_items_list = [line[-1] for line in result_list]
    result_string = "".join(last_items_list)
    result_string =  re.sub(r"%", "", result_string)

    return int(result_string)

def get_tier_links(cvm,userid,tier,curator_master,svmips):

    cmd = "ssh "+cvm+" -l nutanix \"links http:"+curator_master+"/master/tierusage -dump | grep -A 15 \'ILM Down\'\""
    print cmd
    output = subprocess.check_output(cmd, shell=True)
    return parse_output_and_get_total_ssd_usage(output)

def get_tierusage(cvm,userid,tier,svmips):
    curator_master = get_crator_master(cvm,userid,svmips)
    pct = get_tier_links(cvm,userid,tier,curator_master,svmips)
    print "pct"+str(pct) 
    sys.exit(2)
    while curator_master == 'none':
        curator_master = get_crator_master(cvm,userid,svmips)
    curator_master.strip()
    try :
        url =r'http://'+curator_master+'/master/tierusage'
        print url
        tables = pd.read_html(url)
        print tables[1]
        op = tables[1].to_dict()
        print "tier "+str(tier)
        pct = op['Tier Usage Pct'][tier][:-1]
        print op['Tier Usage Pct'][tier]
        print "Current Tier usage is ->> "+str(pct)
        if pct:
            return int(pct)
    except :
        print "Error in get_tierusage"
        #time.sleep(300)
        pct = get_tier_links(cvm,userid,tier,curator_master,svmips)
        if pct:
            return int(pct)


def get_crator_master(cvm,userid,svmips):
    cu_m = 'none'
    run = "ssh "+cvm+" -l "+userid+" \"source /etc/profile; /usr/local/nutanix/bin/curator_cli get_master_location | grep \\\"Master handle\\\"\""
    print run
    cu_m = (os.popen(run).read()).split('|')[2].strip()
    print cu_m
    print '/'+cu_m+'/'
    if cu_m != 'none' :
        return cu_m


def sshCopyid(ip):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    passwd="nutanix/4u"
    cmd = "ssh-keygen -R "+str(ip)
    os.system(cmd)
    try :
        cmd = " /usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@"+str(ip)
        print cmd
        child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no nutanix@%s'%(ip))
        r=child.expect ('you wanted were added.')
        print "Outp"+str(r)
        if r==1:
            cmd = " ssh "+str(ip)+" nutanix -l pwd"
            print cmd
            child = pexpect.spawn('ssh %s nutanix -l pwd'%(ip))
            rsa_key = '\(yes\/no\)\?'
            prompt = "Password:"
            i = child.expect([rsa_key,prompt,""])
            if i==0:
                child.sendline('yes')
                child.expect(prompt)
                child.sendline(passwd)
            elif i==1:
                child.sendline(passwd)
            else:
                child.sendline(passwd)
        child.interact()
        child.close()
    except Exception as e:
        print "Oops Something went wrong buddy"
        #print e


def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    tier = "1"
    cvm = "10.40.225.97"
    sshCopyid(cvm)
    svmips = get_svmips(cvm)
    pct = get_tierusage(cvm,userid,tier,svmips)


if __name__ == "__main__":
    main(sys.argv[1:])


#!/usr/bin/python

import sys, getopt,os,re
import pandas as pd
import random
import string
import time
import itertools
import pexpect
import lxml
from collections import defaultdict

def get_crator_master(cvm,userid,svmips):
    cu_m = 'none'
    """
    run = "ssh "+cvm+" -l "+userid+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    """
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
        print "Nopt able to find curator master "
        sys.exit(2)
    else :
        return cu_m

def get_tierusage(cvm,userid,tier,svmips):
    curator_master = get_crator_master(cvm,userid,svmips)
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
        sys.exit(2)

def get_disklist(cvm,userid):
    diskList = {}
    diskList = defaultdict(list)
    ncli = " /home/nutanix/prism/cli/ncli "
    ssh = "ssh "+cvm+" -l "+userid

    run = ssh +ncli+"disk list | grep Id | grep -v \"Storage Pool Id\"" 
    diskid = (os.popen(run).read()).split('\n')
    #print diskid
    run = ssh +ncli+"disk list | grep \"Controller VM Address\""
    cntrlid = (os.popen(run).read()).split('\n')
    #print cntrlid
    run = ssh +ncli+"disk list | grep \"Mount Path\"" 
    mntpath = (os.popen(run).read()).split('\n')
    #print mntpath
    run = ssh +ncli+"disk list | grep  \"Storage Tier\"" 
    typeD = (os.popen(run).read()).split('\n')
    #print typeD

    for (i,j,k,l) in itertools.izip(diskid,cntrlid,mntpath,typeD):
        if l:
            did = (i.split())[2]
            cid = (j.split(':'))[1]
            dsd = (((k.split(':'))[1]).split('/'))[6]
            typ = (l.split(':'))[1]
            #print did+" "+cid+" "+dsd+" "+typ

            diskList[cid].append({'diskid' :  did ,'typed' :  typ ,'dsid' :  dsd })
    return diskList

def isDiskFailing(cvm):
    ssh = "ssh "+cvm+" -l nutanix"
    ncli = " /home/nutanix/prism/cli/ncli "
    run = ssh +ncli+"disk get-remove-status " 
    op = os.popen(run).read()
    op = op.strip()
    print "Disk fail --> "+op
    if op == '[None]':
        return 0
    else :
        return 1 

def disk_fail(cvm,darray,offset,userid,dtype,tier,svmips,wait):
    ssh = "ssh "+cvm+" -l "+userid
    did = darray[offset]['diskid']
    typed = darray[offset]['typed']
    dsid = darray[offset]['dsid']
    acli = " /usr/local/nutanix/bin/acli -y "
    print did , typed , dsid
    if typed != dtype:
    #if typed != 'SSD-PCIe':
        cmd = ssh+" \"source /etc/profile; /usr/local/nutanix/cluster/bin/disk_operator disk_serial_to_block_device "+dsid+" \""
        print cmd
        op = os.popen(cmd).read()
        match = re.match(r'(.*)Block\s+Device:(.*)', op)
        if match is not None:
            dev  = match.groups()[1] 
            print "The device is --> "+dev
            cmd = ssh+" \"source /etc/profile;  /home/nutanix/prism/cli/ncli disk rm-start force=false id="+did.split(':')[2]+" \""
            print cmd 
            op = os.popen(cmd).read()
            #Disk removal successfully initiated
            mat = re.match(r'Disk\s+removal\s+successfully\s+initiated(.*)', op)
            print mat
            #Disk removal successfully initiated
            cmd = ssh+" \" source /etc/profile; /usr/local/nutanix/apache-cassandra/bin/nodetool -h 0 ring \""
            print cmd 
            os.system(cmd)
            time.sleep(120)
            if mat is not None:
                print "Wait for the disk remove to complete "
                pct = get_tierusage(cvm,userid,tier,svmips)
                if pct > 75:
                    run = "ssh "+cvm+" -l "+userid+" \""+acli+"vm.power_cycle \* \""
                    print run
                    os.system(run)

                while isDiskFailing(cvm):
                    print "Another disk fail is in progress"
                    time.sleep(wait)
                #Successfully repartitioned disk /dev/sdf and added it to zeus
                if not isDiskFailing(cvm):
                    print "Repartion and Add the disk back "
                    cmd = ssh+" \"source /etc/profile; /usr/local/nutanix/cluster/bin/disk_operator --hades_rpc_timeout_secs=60 repartition_add_zeus_disk "+dev +"\""
                    print cmd
                    p = re.compile('Successfully\s+repartitioned\s+disk\s+'+dev+'\s+and\s+added\s+it\s+to\s+zeus')
                    ma = p.match( (os.popen(cmd).read()))
                    if ma is not None:
                        print "Successfully repartitioned disk" 
        else :
            offset = offset+1

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    cvm = ''
    wait=1200
    pct = 0
    tier = 1
    diskfail = 0
    tierusuage = 80
    dtype = 'HDD'
    diskL = {}

    try:
        opts, args = getopt.getopt(argv,"hi:t:d:w:u:f:",["cvm=","tier=","dtype=","wait=","tusuage=","diskflt="])
    except getopt.GetoptError:
        print 'ERROR : tierILM.py -i <cvm> -t<tier : SSD-PCIe - 0 : SSD - 1 > -d <disk type fail SSD/HDD> -w <wait> '
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'USAGE : tierILM.py -i <cvm> -t <tier : SSD-PCIe - 0 : SSD - 1 > -d <disk type fail SSD/HDD> -w <wait> '
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvm = arg
        elif opt in ("-d", "--dtype"):
            dtype = arg
        elif opt in ("-t", "--tier"):
            tier = int(arg)
        elif opt in ("-w", "--wait"):
            wait  = int(arg)
        elif opt in ("-u", "--tusuage"):
            tierusuage  = int(arg)
        elif opt in ("-f", "--diskflt"):
            diskfail  = int(arg)

    acli = " /usr/local/nutanix/bin/acli -y "
    sshCopyid(cvm)
    run = "ssh "+cvm+" -l "+userid+" /usr/local/nutanix/cluster/bin/svmips"
    print run
    output = (os.popen(run).read()).split('\n')
    svmips = output[0].split()
    for  svmip in svmips:
        sshCopyid(svmip)
    if diskfail:
        diskL = get_disklist(cvm,userid)
        nodes = diskL.keys()
    """
    for node in diskL.keys():
        for d in diskL[node]:
            print d['diskid'],d['typed'],d['dsid']
    """
    i=offset=0
    while 1:
        print "Wait -> "+str(wait)+" Tiar usuage limit --> "+str(tierusuage)
        pct = get_tierusage(cvm,userid,tier,svmips)
        if pct < tierusuage:
            run = "ssh "+cvm+" -l "+userid+" \""+acli+"vm.on \* \""
            print run
            os.system(run)
            time.sleep(wait)
        elif pct >= tierusuage and pct <= 85:
            if diskfail:
                if isDiskFailing(cvm):
                    print "Another disk fail is in progress"
                    run = "ssh "+cvm+" -l "+userid+" \""+acli+"vm.power_cycle \* \""
                    print run
                    os.system(run)
                    time.sleep(wait)
                else :
                    if nodes[i] is not None :
                        print "Start the disk Fail Tier iusage is --> "+str(pct)
                        darray = diskL[nodes[i]]
                        disk_fail(nodes[i],darray,offset,userid,dtype,tier,svmips,wait)
                        if i < len(diskL[nodes[i]]):
                            i=i+1
                            offset = offset+1
                        else :
                            i=offset = 0
            else :
                print "The tier usage is heigh --> "+str(pct)
                run = "ssh "+cvm+" -l "+userid+" \""+acli+"vm.off \* \""
                print run
                os.system(run)
                time.sleep(wait)
        elif pct > tierusuage and pct < 85:
            print "The tier usage is heigh --> "+str(pct)
            run = "ssh "+cvm+" -l "+userid+" \""+acli+"vm.power_cycle \* \""
            os.system(run)
        elif pct < tierusuage :
            print "The tier usage is not heigh enough--> "+str(pct)
            run = "ssh "+cvm+" -l "+userid+" \""+acli+"vm.on \* \""
            os.system(run)
        elif pct > 85:
            print "The tier usage is heigh --> "+str(pct)
            run = "ssh "+cvm+" -l "+userid+" \""+acli+"vm.off \* \""
            print run
            os.system(run)

        time.sleep(wait)

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

if __name__ == "__main__":
    main(sys.argv[1:])


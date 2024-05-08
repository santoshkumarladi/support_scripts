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
from collections import defaultdict
from datetime import datetime, timedelta

def totimestamp(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6 


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
            run = "ssh "+cvm+" -l "+userid+" \"source /etc/profile; /usr/local/nutanix/bin/curator_cli get_master_location | grep \\\"Master handle\\\"\""
            print run
            #cu_m = (os.popen(run).read()).split('|')[2].strip()
            cu_m = (os.popen(run).read()).split('|')[2].strip()
            print cu_m
            print '/'+cu_m+'/'
            if cu_m != 'none' :
                return cu_m

    if cu_m == 'none' :
        print "Not able to find curator master "
        time.sleep(300)
    else :
        print "----------------> "+cu_m
        return cu_m

def get_tierusage(cvm,userid,tier,svmips):
    curator_master = get_crator_master(cvm,userid,svmips)
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
        #sys.exit(2)
        time.sleep(300)
        get_tierusage(cvm,userid,tier,svmips)

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
    run = ssh +ncli+"disk list | grep  \"Online\"" 
    stateD = (os.popen(run).read()).split('\n')

    for (i,j,k,l,m) in itertools.izip(diskid,cntrlid,mntpath,typeD,stateD):
        if l:
            did = (i.split())[2]
            cid = (j.split(':'))[1]
            dsd = (((k.split(':'))[1]).split('/'))[6]
            typ = (l.split(':'))[1]
            ste = (m.split(':'))[1]
            #print did+" "+cid+" "+dsd+" "+typ

            diskList[cid].append({'diskid' :  did ,'typed' :  typ ,'dsid' :  dsd ,'online' : ste })
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

def disk_fail(cvm,darray,offset,userid,dtype,tier,svmips,last_diskfail,wait):

    last_diskfail = int (totimestamp(datetime.now())) 
    ssh = "ssh "+cvm+" -l "+userid
    did = darray[offset]['diskid']
    typed = darray[offset]['typed']
    dsid = darray[offset]['dsid']
    state = darray[offset]['online'] 
    
    acli = " /usr/local/nutanix/bin/acli -y "
    typed.rstrip()
    state.rstrip()
    #0005bd95-b782-587c-38dc-ac1f6b3b46cf::41  SSD S456NY0M908592  true SDD  true 
    #00059d2f-a53f-cff6-0000-000000025559::5641742642 HDD ZC17Y741  true HDD    true 
    #print did+" typed"+typed+" "+dsid+" state"+state+" dtype"+dtype+" state"+state+" "
    typed = typed.lstrip()
    state = state.lstrip()
    print " typed "+typed.lower()+" dtype "+dtype.lower()
    if typed.lower() == dtype.lower() and 'true' in state.lstrip():
    #and 'true' in state.lstrip():
    #if 'true' in state.lstrip():
    #if  'true' in state:
    #if typed != 'SSD-PCIe':
        print "Disk is Online --> "+state
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
                    last_diskfail = last_diskfail+wait
                    time.sleep(wait)
                    print " last_diskfail -> "+str(last_diskfail)
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
                print "Disk Removal output --> "+op
                offset = offset+1
        else :
            offset = offset+1

    return last_diskfail

def get_failnode(cvm,svmips):
    acli = " /usr/local/nutanix/bin/acli -y "
    ssh = "ssh "+cvm+" -l nutanix"

    run = ssh +acli+"host.list "
    print run

    op = os.popen(run).read()
    op = op.strip()
    print "Op ---> "+op
    if op :
        output = op.split('\n')
        for i in range(1,len(output)-1):
            print output[i].split()[3]
            if output[i].split()[3] != 'AcropolisNormal':
                print output[i].split()[-1]
                return output[i].split()[-1]
        return 'None'

    else :
        print "return the down cvm -- > "+cvm
        return cvm


def get_svmips(cvm):
    #run = "ssh "+cvm+" -l nutanix /usr/local/nutanix/cluster/bin/svmips"
    #print run
    #output = (os.popen(run).read()).split('\n')
    #svmips = output[0].split()
    #return svmips 
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


def main(argv):
    global last_diskfail
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
    disk_fail_count=0
    buftime = 28800

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
    last_diskfail=0

    svmips = get_svmips(cvm)
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
        svmips = get_svmips(cvm)
        pct = get_tierusage(cvm,userid,tier,svmips)
        offNode= get_failnode(cvm,svmips)
        if offNode == '[None]' :
            print "No node detach / fail is running "
        else :
            print "Fail node  --> "+offNode

        if  offNode == cvm :
            print "Fail node and test CVM are same --> "+offNode
            vmips = svmips.remove(cvm)
            print "Removed the fail node from the list --> "+vmips
            cvm = random.shuffle(svmips).pop
            print "New test CVM  --> "+cvm

        if pct < tierusuage:
            run = "ssh "+cvm+" -l "+userid+" \""+acli+"vm.on \* \""
            print run
            os.system(run)
            time.sleep(wait)
        elif pct >= tierusuage and pct <= 85:
            print totimestamp(datetime.now())
            if diskfail:
                current = int (totimestamp(datetime.now()))

                if isDiskFailing(cvm):
                    print "Another disk fail is in progress"
                    run = "ssh "+cvm+" -l "+userid+" \""+acli+"vm.power_cycle \* \""
                    print run
                    os.system(run)
                    time.sleep(wait)
                    last_diskfail = int (totimestamp(datetime.now()))+wait
                    print "currtn -> "+str(current)+" last_diskfail -> "+str(last_diskfail)

                else :
                    print "currtn -> "+str(current)+" last_diskfail -> "+str(last_diskfail)
                    if current > last_diskfail+buftime:
                        if nodes[i] is not None :
                            print "Start the disk Fail Tier iusage is --> "+str(pct)
                            if nodes[i] == offNode :
                                print "Off node --> "+nodes[i]
                                i=i+1
                            else :
                                darray = diskL[nodes[i]]
                                last_diskfail = disk_fail(nodes[i],darray,offset,userid,dtype,tier,svmips,last_diskfail,wait)
                                disk_fail_count = disk_fail_count+1
                                print "Disk Fail count ---> "+str(disk_fail_count)
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
            print "The tier usage is heigh > 85 --> "+str(pct)
            run = "ssh "+cvm+" -l "+userid+" \""+acli+"vm.off \* \""
            print run
            os.system(run)

        print "No condition met going to sleep --> "+str(pct)
        time.sleep(wait)

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
        #print e


if __name__ == "__main__":
    main(sys.argv[1:])


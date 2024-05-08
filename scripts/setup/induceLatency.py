#!/usr/bin/python

import sys, getopt,os,re
import pexpect
import string
import time
import subprocess


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
            if output[i].split()[3] == 'AcropolisNormal' :
                svmips.append(output[i].split()[-1])
        return svmips

def induce_latency(ssh, delay, delay_buffer, duration, num_iterations=1, interface="eth0", wait_between_iterations=300):
    try:

        # Construct the full command to check existing network emulation settings
        check_cmd = "sudo tc qdisc show dev %s" % interface

        # Construct the full command to add network emulation settings
        add_cmd = "sudo tc qdisc add dev %s root netem delay %sms %sms " % (interface, delay, delay_buffer)
        add_cmd += " && sleep %s" % duration
        add_cmd += " && sudo tc qdisc del dev %s root" % interface  # Remove the added latency

        for i in range(num_iterations):
            # Construct the SSH command to execute on the remote client
            ssh_check_command = "%s '%s'" % (ssh, check_cmd)
            ssh_add_command = "%s '%s'" % (ssh, add_cmd)
            
            # Execute the SSH command to check existing settings
            check_output = subprocess.check_output(ssh_check_command, shell=True)
            print check_output
            # Check if there are existing settings
            if "netem" in check_output:
                # Existing settings found, remove them before adding new settings
                subprocess.call(ssh_check_command, shell=True)  # Ensure the output is displayed
                check_output = subprocess.call(ssh_add_command, shell=True)
                print check_output

            else:
                # No existing settings found, directly add new settings
                print ssh_add_command
                check_output = subprocess.call(ssh_add_command, shell=True)
                print check_output

            print "Latency of %sms (+/-%sms) induced on interface %s of remote client %s." % (delay, delay_buffer, interface, ssh)
            print "Waiting for %s seconds..." % duration
            time.sleep(duration)

            if i < (num_iterations - 1):
                print "Waiting %s seconds before next iteration..." % wait_between_iterations
                time.sleep(wait_between_iterations)

        # Remove the added latency settings after the last iteration
        remove_cmd = "sudo tc qdisc del dev %s root" % interface
        ssh_remove_command = "%s '%s'" % (ssh, remove_cmd)
        check_output = subprocess.call(ssh_remove_command, shell=True)
        print("Latency removed from interface %s of remote client %s op of cmd %s." % (interface, ssh, check_output))


    except subprocess.CalledProcessError as e:
        print "Error: Failed to induce latency: %s" % e



def sshCopyid(ip,userid,passwd):
    #ssh-copy-id -f -i ~/.ssh/id_rsa.pub  -o "StrictHostKeyChecking no" nutanix@10.46.141.102
    #passwd="nutanix/4u"
    rsa_key = '\(yes\/no\)\?'
    prompt = "assword:"
    non_rsa='you wanted were added.'

    cmd = "ssh-keygen -R "+str(ip)
    print cmd
    os.system(cmd)
    cmd = " /usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no "+userid+"@"+str(ip)
    print cmd
    child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i /home/santoshkumar.ladi/.ssh/id_rsa.pub -o StrictHostKeyChecking=no %s@%s'%(userid,ip))
    #r=child.expect ('you wanted were added.')
    r= child.expect([non_rsa,rsa_key,prompt,pexpect.EOF],timeout=30)
    print "Outp"+str(r)
    if r==0:
        print "Outp 0"
        child.interact()
        child.close()
    elif r==1:
        print "Outp 1"
        child.sendline('yes')
        child.expect(prompt)
        child.sendline(passwd)
    elif r==2:
        print "Outp 2"
        child.sendline(passwd)
    elif r==3:
        print "Outp 3"
        child.sendline(passwd)
        child.interact()
        child.close()
    else :
        print "Outp 4"
        child.expect(prompt)
        child.sendline(passwd)

    child.interact()
    child.close()

def main(argv):
    userid = 'nutanix'
    passwd = 'nutanix/4u'
    cmd = ''
    wait = 30
    delay = 100
    delay_buffer = 20
    duration = 300
    num_iterations = 1
    interface = "eth0"

    try:
        opts, args = getopt.getopt(argv,"hi::n:p:w:",["cvm=","noiter=","passwd=","wait="])
    except getopt.GetoptError:
        print 'runTest.py -i <cvm> -n <num_iterations> -w <wait>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'runTest.py -i <cvm> -n <num_iterations> -w <wait>'
            sys.exit()
        elif opt in ("-i", "--cvm"):
            cvm = arg
        elif opt in ("-n", "--noiter"):
            num_iterations = int(arg)
        elif opt in ("-p", "--passwd"):
            passwd = arg
        elif opt in ("-w", "--wait"):
            wait = int(arg)


    svmips =  get_svmips(cvm)
    for  svmip in svmips:
        print svmip
        sshCopyid(svmip,userid,passwd)

    for  svmip in svmips:
        ssh = "ssh "+svmip+" -l "+userid
        # Call the function to induce latency on the remote client
        induce_latency(ssh, delay, delay_buffer, duration, num_iterations, interface, wait)


if __name__ == "__main__":
    main(sys.argv[1:])


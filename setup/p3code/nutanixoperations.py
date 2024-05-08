import os,re
import random
import string
import time
import pexpect
import subprocess
import json
import argparse
from datetime import datetime, timedelta

class NutanixClusterOperations:
    def __init__(self, cvm_ip, userid, passwd):
        self.cvm_ip = cvm_ip
        self.userid = userid
        self.passwd = passwd
        self.ssh_copy_id(cvm_ip)
        #self.svm_ips = self.get_svm_ips()

    def get_svm_ips(self):
        svm_ips = []
        acli = "/usr/local/nutanix/bin/acli -y"
        ssh = "ssh " + self.cvm_ip + " -l nutanix "
        run = ssh + acli + " host.list"
        print(run)

        op = os.popen(run).read()
        op = op.strip()
        print("Op ---> " + op)
        if op:
            output = op.split('\n')
            for i in range(1, len(output)):
                #if output[i].split()[4] != 'False' and output[i].split()[6] != 'False':
                if output[i].split()[3] == 'AcropolisNormal' and output[i].split()[6] != 'False':
                    svm_ips.append(output[i].split()[-1])
                    self.ssh_copy_id(output[i].split()[-1])

        return svm_ips

    def ssh_copy_id(self,ip):
        home_dir = os.path.expanduser("~")
        ssh_pub_key = os.path.join(home_dir, ".ssh/id_rsa.pub")
        rsa_key = '\(yes\/no\)\?'
        prompt = "assword:"
        non_rsa = 'you wanted were added.'

        cmd = "ssh-keygen -R " + str(ip)
        print(cmd)
        os.system(cmd)

        cmd = " /usr/bin/ssh-copy-id -f -i " + ssh_pub_key + " -o StrictHostKeyChecking=no " + self.userid + "@" + str(ip)
        print(cmd)
        child = pexpect.spawn('/usr/bin/ssh-copy-id -f -i ' + ssh_pub_key + ' -o StrictHostKeyChecking=no %s@%s' % (self.userid, ip))

        r = child.expect([non_rsa, rsa_key, prompt, pexpect.EOF], timeout=30)
        print("Outp" + str(r))

        if r == 0:
            print("Outp 0")
            child.interact()
            child.close()
        elif r == 1:
            print("Outp 1")
            child.sendline('yes')
            child.expect(prompt)
            child.sendline(self.passwd)
        elif r == 2:
            print("Outp 2")
            child.sendline(self.passwd)
        elif r == 3:
            print("Outp 3")
            child.sendline(self.passwd)
            child.interact()
            child.close()
        else:
            print("Outp 4")
            child.expect(prompt)
            child.sendline(self.passwd)

        child.interact()
        child.close()

    def run_cmd_remote(self, cmd, remote_host):
        try:
            # Construct the SSH command to run the Python code remotely
            ssh_command = f"ssh {self.userid}@{remote_host} \"{cmd}\""
            print("SSH Command:", ssh_command)

            # Run the SSH command to execute the code on the remote machine
            result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)

            # Check if the command was successful
            if result.returncode != 0:
                print("Error running code remotely:")
                print(result.stderr)
                return {}

            # Get the output from the SSH command
            output = result.stdout.strip()
            print("Output:")
            #print(output)
            print(result.stderr)

            # Check if the output is empty
            if not output:
                print("Error: Empty output received.")
                return {}
            else :
                return output
        except subprocess.CalledProcessError as e:
            print(f"Error running code remotely: {e}")
            return {}

    def run_python_code_remote(self, python_code, remote_user, remote_host):
        try:
            # Construct the SSH command to run the Python code remotely
            ssh_command = f"ssh {remote_user}@{remote_host} \"python3.6 -c \\\"{python_code}\"\\\""
            #print("SSH Command:", ssh_command)

            # Run the SSH command to execute the code on the remote machine
            result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)

            # Check if the command was successful
            if result.returncode != 0:
                print("Error running code remotely:")
                print(result.stderr)
                return {}

            # Get the output from the SSH command
            output = result.stdout.strip()
            #print("Output:")
            #print(output)

            # Check if the output is empty
            if not output:
                print("Error: Empty output received.")
                return {}

            # Try to load the output as JSON
            try:
                process_dict = json.loads(output)
                return process_dict
            except json.JSONDecodeError as e:
                print("Error decoding JSON output:", e)
                return {}

        except subprocess.CalledProcessError as e:
            print(f"Error running code remotely: {e}")
            return {}


    def get_services(self,cvm):
        services =  []
        cmd = " source /etc/profile; /usr/local/nutanix/cluster/bin/genesis status "
        print (cmd)
        op = self.run_cmd_remote(cmd, cvm) 
        print("-----------------")
        #print (op)
        output = op.split('\n')
        for i in range(1,len(output)-1):
            #print (output[i].split(':')[0].strip())
            services.append(output[i].split(':')[0].strip())
        return services


    def get_process(self,svmips,process_names,wait):
        python_code = f"""
import psutil
import json
import os

def get_pids_by_name(process_name):
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name in proc.info['name']:
            pids.append(proc.info['pid'])

    cmd = f\\\\\\"source /etc/profile; /usr/local/nutanix/cluster/bin/genesis status | grep -E {{process_name}}\\\\\\"
    if len(pids) < 1:
        op = os.popen(cmd).read()
        op = op.split('\\n')
        for proc in op:
            if proc:
                pds = json.loads(proc.split(':')[1].strip())
                for pid in pds:
                    pids.append(pid)
    return pids

def get_process_names_with_pids():
    process_dict = {{}}
    process_names = {process_names}
    for name in process_names:
        pids = get_pids_by_name(name)
        process_dict[name] = pids
    return process_dict

result_dict = get_process_names_with_pids()
print(json.dumps(result_dict))

"""
        result_dict = {}
        for remote_host in svmips:
            # Run the Python code remotely and get the process dictionary
            result_dict[remote_host] = self.run_python_code_remote(python_code, self.userid, remote_host)
            
            # Print the dictionary with process names and corresponding PIDs
            #print("Process Dictionary:")
            print(result_dict[remote_host])
        return result_dict


    def kill_service(self,host,pids):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pids_str = " ".join(str(pid) for pid in pids)
        cmd = f" kill -9 {pids_str}" 
        print(f"Process with PID {pids_str} killed at {current_time}")
        self.run_cmd_remote(cmd, host) 
        

    def vm_create_large(self, run, vmcount, patern, bdisksize, vcpus, disks, hostlist, containername, edisksize, imgp, userid, vlan, remote, pd):
        ncli = "ssh " + self.cvm_ip + " -l " + userid + " /home/nutanix/prism/cli/ncli "
        vmList = []
        nosnap = 8
        j = k = 0

        for i in range(vmcount):
            if imgp[j] == 'oltpS':
                memory = '4G'
                vdisks = 6
                vdisk_size = '32G'
                vcpu = 4
                cores = 1
            elif imgp[j] == 'fioS':
                memory = '8G'
                vdisks = 8
                vdisk_size = '20G'
                vcpu = 4
                cores = 2
            elif imgp[j] == 'vdbS':
                memory = '4G'
                vdisks = 4
                vdisk_size = '300G'
                vcpu = 2
                cores = 1
            elif imgp[j] == 'strS':
                memory = '8G'
                vdisks = 16
                vdisk_size = '52G'
                vcpu = 8
                cores = 1
            elif imgp[j] == 'winS':
                memory = '4G'
                vdisks = 8
                vdisk_size = '52G'
                vcpu = 4
                cores = 2
            elif imgp[j] == 'tiltS':
                memory = '8G'
                vdisks = 8
                vdisk_size = '50G'
                vcpu = 4
                cores = 1
            elif imgp[j] == 'largS':
                memory = '4G'
                vdisks = 1
                vdisk_size = edisksize
                vcpu = 4
                cores = 1
            elif imgp[j] == 'vgcS':
                memory = '8G'
                vdisks = 1
                vdisk_size = edisksize
                vcpu = 4
                cores = 1

            if disks:
                vdisks = disks

            vmname = patern + imgp[j] + "_largevm_" + str(random.randint(100, 128908))
            cmd = run + " vm.create " + vmname + " memory=" + memory + " num_vcpus=" + str(vcpu) + " num_cores_per_vcpu=" + str(cores)
            print(cmd)
            os.system(cmd)

            cmd = run + " vm.disk_create " + vmname + " clone_from_image=" + imgp[j]
            print(cmd)
            os.system(cmd)

            cmd = run + " vm.nic_create " + vmname + " network=" + vlan
            print(cmd)
            os.system(cmd)

            cmd = run + " vm.on " + vmname
            print(cmd)
            os.system(cmd)

            k = k + 1 if k < len(containername) - 1 else 0
            for i in range(vdisks):
                cmd = run + " vm.disk_create " + vmname + " container=" + containername[k] + " create_size=" + vdisk_size
                print(cmd)
                os.system(cmd)

            if pd:
                self.pd_create(ncli, vmname, nosnap, remote)

            cmd = run + " vm.on " + vmname
            print(cmd)
            os.system(cmd)

            vmList.append(vmname)
            if j < len(imgp) - 1:
                j = j + 1
            else:
                j = 0

        time.sleep(30)
        for vm in vmList:
            self.set_up_lvm(run, "nutanix/4u", vm)

        cmd = run + " vm.power_cycle " + patern + imgp[j] + "_largevm_" + "*"
        print(cmd)
        os.system(cmd)

    def pd_create(self, ncli, vmname, nosnap, remote):
        # Define your pd_create function here
        pass

    def set_up_lvm(self, run, container, vmname):
        # Define your set_up_lvm function here
        pass

    def pdCreates(self, cvm, vmname, remote, near):
        ncli = " /home/nutanix/prism/cli/ncli "
        ssh = "ssh " + cvm + " -l nutanix"
        acli = ssh + " /usr/local/nutanix/bin/acli -y"
        if '*' in vmname:
            cmd = acli + " vm.list | grep -v auto | grep -v ltss "
            print(cmd)
        else:
            cmd = acli + " vm.list | grep -v auto | grep -v ltss | grep \"" + vmname + "\""
            print(cmd)
        output = (os.popen(cmd).read()).split('\n')
        print(output)
        for i in range(1, len(output) - 1):
            (vm, uuid) = output[i].split()
            if len(vm) > 70:
                vm = vm[:60]
            run = ssh + ncli
            cmd = run + " pd create name=testPD_" + vm
            print(cmd)
            os.system(cmd)
            cmd = run + " pd protect name=testPD_" + vm + " vm-names=" + vm + " cg-name=testCG" + vm
            print(cmd)
            os.system(cmd)
            print("_______________________________________> " + str(remote) + " -- nearsync " + str(near))
            nosnap = 8
            cmd = run + "\" pd clear-schedules name=testPD_" + vm.strip() + "\""
            print(cmd)
            os.system(cmd)

            if near:
                cmd = run + "\" pd add-minutely-schedule name=testPD_" + vm + " local-retention-type=DAYS every-nth-minute=15 remote-retention=" + str(remote) + " remote-retention-type=" + near + " start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
                print(cmd)
                os.system(cmd)
            if remote:
                cmd = run + "\" pd add-hourly-schedule name=testPD_" + vm + " local-retention=" + str(
                    nosnap) + " remote-retention=" + str(remote) + " every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
                print(cmd)
                os.system(cmd)
                remote = ','.join([i.split(':')[0] for i in remote.split(',') if i])
                cmd = run + "\" pd create-one-time-snapshot remote-sites=" + remote + " name=testPD_" + vm + " retention-time=" + str(random.randint(100, 128)) + "\""
                print(cmd)
                os.system(cmd)
            else:
                cmd = run + "\" pd add-hourly-schedule name=testPD_" + vm + " local-retention=" + str(
                    nosnap) + " every-nth-hour=1 start-time=\\\"02/14/2018 12:30:00 UTC\\\"\""
                print(cmd)
                os.system(cmd)
            nosnap = 10
            cmd = run + "\" pd add-hourly-schedule name=testPD_" + vm + " local-retention=" + str(
                nosnap) + " every-nth-hour=6 start-time=\\\"02/14/2018 18:30:00 UTC\\\"\""
            print(cmd)
            os.system(cmd)
            nosnap = 5
            cmd = run + "\" pd add-daily-schedule name=testPD_" + vm + " local-retention=" + str(
                nosnap) + " start-time=\\\"02/14/2018 09:30:00 UTC\\\"\""
            print(cmd)
            os.system(cmd)

    def generate_random_string(self):
        characters = string.ascii_letters + string.digits 
        return ''.join(random.choice(characters) for _ in range(1024))

    def updateVmbyPattern(self, ssh, cvm, vname):
        run = ssh + " vm.list | grep -v auto | grep -v ltss | grep -E \"" + vname + "|update\" "
        print(run)
        output = (os.popen(run).read()).split('\n')
        print(output)

        for i in range(0, len(output) - 1):
            (vm, uuid) = output[i].split()
            cmd = ssh + " vm.update " + vm + " name=update" + str(self.generate_random_string())
            print(cmd)
            os.system(cmd)

    def get_clusterDetails(self, cvm):
        cluster_details = {}

        ncli = " /home/nutanix/prism/cli/ncli "
        ssh = "ssh " + cvm + " -l nutanix"
        run = ssh + ncli + "cluster info "
        print(run)
        ctr = os.popen(run).read()
        if ctr:
            ctr = ctr.split('\n')
            for ctrN in ctr:
                if ctrN:
                    (key, val) = ctrN.split(" : ")
                    key = key.strip()
                    cluster_details[key] = val
                    # print "key "+str(key)+" val "+str(val)
        return cluster_details


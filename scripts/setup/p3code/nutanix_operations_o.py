mport os
import random
import string
import time

class NutanixClusterOperations:
    def __init__(self, cvm_ip, userid, passwd):
        self.cvm_ip = cvm_ip
        self.userid = userid
        self.passwd = passwd
        self.svm_ips = self.get_svm_ips()
        self.ssh_copy_id()

    def get_svm_ips(self):
        svm_ips = []
        acli = "/usr/local/nutanix/bin/acli -y"
        ssh = "ssh " + self.cvm_ip + " -l nutanix"
        run = ssh + acli + " host.list"
        print(run)

        op = os.popen(run).read()
        op = op.strip()
        print("Op ---> " + op)
        if op:
            output = op.split('\n')
            for i in range(1, len(output)):
                if output[i].split()[4] != 'False' and output[i].split()[6] != 'False':
                    svm_ips.append(output[i].split()[-1])

        return svm_ips

    def ssh_copy_id(self):
        home_dir = os.path.expanduser("~")
        ssh_pub_key = os.path.join(home_dir, ".ssh/id_rsa.pub")
        rsa_key = '\(yes\/no\)\?'
        prompt = "assword:"
        non_rsa = 'you wanted were added.'

        for ip in self.svm_ips:
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

    def vm_create_small(cls, run, cvm, vmcount, patern, hostlist, containername, userid, vlan, remote, pd):
        ncli = "ssh " + cvm + " -l " + userid + " /home/nutanix/prism/cli/ncli "
        vm_list = []
        nosnap = 8
        k = 0
        imgp = 'fioS'
        memory = '2G'
        vdisks = 1
        vdisk_size = '20G'
        vcpu = 2
        cores = 1

        for i in range(vmcount):
            vmname = patern + imgp + "_smallvm_" + str(random.randint(100, 128908))
            cmd = run + " vm.create " + vmname + " memory=" + memory + " num_vcpus=" + str(vcpu) + " num_cores_per_vcpu=" + str(cores)
            print(cmd)
            os.system(cmd)

            cmd = run + " vm.disk_create " + vmname + " clone_from_image=" + imgp
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

            cmd = run + " vm.on " + vmname
            print(cmd)
            os.system(cmd)

            vm_list.append(vmname)

        if pd:
            cls.pd_create_mul(ncli, vm_list, nosnap, "smallvm", remote)

    def pd_create_mul(cls, ncli, vm_list, nosnap, vm_type, remote):
        # Implement your pd_create_mul method logic here
        pass

    def set_up_lvm(cls, ssh, passwd, cvm, vmname):
        sc_home_path = os.path.join(home_dir, "scripts/setup")
        ip = ''
        dev_list = []
        ncli = "ssh " + cvm + " -l nutanix /home/nutanix/prism/cli/ncli "
        run = ncli + " vm list name=" + vmname + " | grep \"VM IP Addresses\""
        print(run)
        match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
        if match is not None:
            ip = match.group()
            print(vmname + "  " + ip)
        else:
            cmd = ssh + " vm.power_cycle " + vmname
            print(cmd)
            os.system(cmd)
            time.sleep(120)
            run = ncli + " vm list name=" + vmname + " | grep \"VM IP Addresses\""
            print(run)
            match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', (os.popen(run).read()))
            if match is not None:
                ip = match.group()
                print(vmname + "  " + ip)
        if ip:
            cls.ssh_copy_id(ip, "root", passwd)
            cmd = "scp -r "+sc_home_path+"/setupLargeClient.sh root@" + str(ip) + ":/home/nutanix/"
            print(cmd)
            os.system(cmd)
            cmd = "scp -r "+sc_home_path+"/setup/rc.local root@" + str(ip) + ":/etc/rc.d/rc.local"
            print(cmd)
            os.system(cmd)
            cmd = "ssh " + ip + " -l root \"sudo chmod +x /etc/rc.d/rc.local\""
            print(cmd)
            os.system(cmd)

    def run_python_script_remote(script_path, process_names, remote_user, remote_host):
        try:
            # Construct the SSH command to run the Python script remotely
            ssh_command = f"ssh {remote_user}@{remote_host} 'python3 -c \"import {script_path.stem} as script; print(json.dumps(script.get_process_names_with_pids({process_names})))\"'"
    
            # Run the SSH command to execute the script on the remote machine
            result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, check=True)

            # Convert the JSON output to a Python dictionary
            output = result.stdout.strip()
            process_dict = json.loads(output)

            return process_dict
        except subprocess.CalledProcessError as e:
            print(f"Error running script remotely: {e}")
            return {}


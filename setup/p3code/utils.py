import os
import json
import time
import random
import string
import socket
import pexpect
import argparse
import paramiko
import subprocess

class NutanixClusterOperations:
    def __init__(self,hostname, port, username, password=None, key_filename=None):
        self.cvm_ip = cvm_ip
        self.userid = userid
        self.passwd = passwd
        self.ssh_copy_id(cvm_ip)
        #self.svm_ips = self.get_svm_ips()
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.client = None
        self.channel = None

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if self.key_filename:
                self.client.connect(self.hostname, port=self.port, username=self.username,
                                    key_filename=self.key_filename, timeout=10)
            else:
                self.client.connect(self.hostname, port=self.port, username=self.username,
                                    password=self.password, timeout=10)
            self.channel = self.client.invoke_shell()
            return True, None
        except paramiko.AuthenticationException as auth_err:
            return False, f"Authentication failed: {auth_err}"
        except paramiko.SSHException as ssh_err:
            return False, f"SSH connection failed: {ssh_err}"
        except socket.timeout as timeout_err:
            return False, f"Connection timeout: {timeout_err}"
        except Exception as e:
            return False, f"Error connecting to SSH: {e}"

    def execute_command(self, command, timeout=60):
        if not self.client:
            return False, None, "SSH connection is not established. Call connect() first."

        try:
            self.channel.send(command + '\n')
            time.sleep(1)  # Wait for command to execute
            output = ''
            start_time = time.time()
            while not output.endswith('$ ') and time.time() - start_time < timeout:
                if self.channel.recv_ready():
                    output += self.channel.recv(1024).decode('utf-8')
                else:
                    time.sleep(1)
            return True, output, None
        except Exception as e:
            return False, None, f"Error executing command: {e}"

    def handle_failures(self, success, output, error):
        if success:
            print("Command executed successfully. Output:")
            print(output)
        else:
            print(f"Failed to execute command: {error}")

    def get_svm_ips(self):
        svm_ips = []
        acli = "/usr/local/nutanix/bin/acli -y"
        command = acli + " host.list"
        print("Command to execute:", command)

        success, output, error = self.execute_command(command)

        if success:
            output = output.strip()
            print("Output ---> ", output)
            if output:
                lines = output.split('\n')
                for line in lines[1:]:
                    columns = line.split()
                    if columns[4] != 'False' and columns[6] != 'False':
                        svm_ips.append(columns[-1])
                        self.ssh_copy_id(columns[-1])
        else:
            print(f"Failed to execute command: {error}")

        return svm_ips

    def close(self):
        if self.client:
            self.client.close()



    def run_python_code_remote(self, python_code, remote_user, remote_host):
        try:
            # Construct the SSH command to run the Python code remotely
            ssh_command = f" python3.6 -c \\\"{python_code}\\\""
            #print("SSH Command:", ssh_command)

            # Run the SSH command to execute the code on the remote machine
            success, result, error = self.execute_command(command)

            # Check if the command was successful
            if error:
                print("Error running code remotely:")
                print(error)
                return {}

            # Get the output from the SSH command
            output = result.strip()
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

    def get_process(self,svmips,process_names,wait):
        python_code = f"""
import psutil
import json

def get_pids_by_name(process_name):
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            pids.append(proc.info['pid'])
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
        for remote_host in svmips:
            # Run the Python code remotely and get the process dictionary
            result_dict = {remote_host : self.run_python_code_remote(python_code, self.userid, remote_host)}
            
            # Print the dictionary with process names and corresponding PIDs
            print("Process Dictionary:")
            print(result_dict)
        return result_dict


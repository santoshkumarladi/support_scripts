import ssl
#import certifi

from myrestlib import SSHRestAPIConnection

# Disable SSL certificate verification
#ssl._create_default_https_context = ssl._create_unverified_context
# Load the system's trusted SSL certificates
#ssl_context = ssl.create_default_context(cafile=certifi.where())

# Define the SSHRestAPIConnection object
conn = SSHRestAPIConnection('10.5.16.147', 'admin', 'Nutanix.123')

# Define the command to execute
cmd = 'ncli --json=true vm list'

# Execute the command and get the output
output = conn.execute_command(cmd)

# Parse the output as JSON
vm_list = []
for vm in output['data']:
    vm_list.append(vm['vmName'])

# Print the list of VM names
print('List of VMs:')
for vm_name in vm_list:
    print(vm_name)


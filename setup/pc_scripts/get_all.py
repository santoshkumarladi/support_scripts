import sys,getopt
import random
import itertools
from utils import NutanixConnection
from collections import defaultdict

# Nutanix Prism Central details
#pc_ip = "10.5.16.147"


# Create a NutanixConnection object

def categories_list(connection):
    # Get categories
    # Define the payload
    categoryl = (connection.get_categories_list())["entities"]
    #print (categoryl)
    for category in categoryl:
        if isinstance (category,dict) and "testSPCategory" in category["name"]:
            value = "c"+(category["name"]).split("testSPCategory")[1]
            categoryl.extend({"name":category["name"],"value":value})
            print(category["name"])
    return categoryl

def sp_stress(connection,sp_iter):

    spolicyl = (connection.get_sp_list(payload))["entities"]
    for stoagep in spolicyl:
        #print(stoagep["status"]["name"])
        if isinstance (stoagep,dict) and "testSpolicy" in stoagep["status"]["name"]:
        #if "testSpolicy" in stoagep["status"]["name"]:
            spolicyl.extend({"name":stoagep["status"]["name"],"uuid":stoagep["metadata"]["uuid"]})

    if len(spolicyl) > 1:
        for stoagep in spolicyl:
            print(stoagep["metadata"]["uuid"])
            connetcion.del_sp(stoagep["metadata"]["uuid"])

def configure_category_sp(connection,batch_size,sp_iter):

    # Get clusters
    # Define the payload
    #payload = {
    #    'kind': 'cluster'
    #}

    #clusters = (connection.get_clusters(payload))["entities"]
    #for cluster in clusters:
    #    cluster_name = cluster["status"]["name"]
    #    cluster_uuid = cluster["metadata"]["uuid"]
    #    print(f"Cluster Name: {cluster_name}")
    #    print(f"Cluster UUID: {cluster_uuid}")
    #print()

    categoryl = categories_list(connection) 

    #sys.exit()
    # Get VMs
    # Define the payload
    vm_payload = {
        'kind': 'vm',
        'offset': 0,
        'length': 1000
    }
    vms = (connection.get_vms(vm_payload))["entities"]
    res ={}
    # Split the list into batches of 10
    for vm in vms:
        res[vm["metadata"]["uuid"]] = vm["status"]["name"]
    resk = list(res.keys())
    #batch_size = 5
    vm_batches = [resk[i:i+batch_size] for i in range(0, len(resk), batch_size)]

    # Iterate over each batch and add the category
    #category_uuid = "your_category_uuid"
    for vm_batch in vm_batches:
        vm_payload = {
            "spec":{
                "resources":{}
            },
            "metadata":{ 
                "categories_mapping":{
                },
                "categories":{
                },
                "kind":"mh_vm",
                "spec_version": 0
            }
        }
        if len(categoryl) < 1: 
            rand = str(random.randint(100,128908))
            category_name = "testSPCategory"+str(rand)
            sp_name = "testSpolicy"+str(rand)
            value = "c"+str(rand)
            resp = connection.create_category(category_name)
            resp = connection.update_category_value(category_name,value)
            #categories = connection.get_category(category_name,payload)
        else:
            category = categoryl.pop()
            category_name = category["name"]
            value = category["value"]

        resp = connection.create_strpol(sp_name,category_name,value)
        #print (categories)
        for key in vm_batch : 
            vm_payload['metadata']['categories'][category_name] = value
            #vm_names = [res[key] for key in vm_batch]
            vmspec = connection.get_vm(key)
            print ("Current spec version of vm {key} - {vmspec['metadata']['spec_version']}")
            vm_payload['metadata']['spec_version'] = vmspec['metadata']['spec_version']
            #vm_uuid = [vm["metadata"]["uuid"] for vm in vm_batch]
            #names = [vm_names[i:i+1] for i in range(0, len(vm_names), 1)]
            vm_payload['metadata']['categories_mapping'][category_name] = (res[key]).split()
            #print (vm_payload)
            connection.add_vm_to_category(key, category_name, vm_payload)
        #for (name,uuid) in zip(names,vm_uuid):
        #vm_payload['metadata']['categories_mapping'] = defaultdict(list, vm_payload['metadata']['categories_mapping'])
        #vm_payload['metadata']['categories_mapping'][category_name] = name
        #print (vm_payload)
        #connection.add_vm_to_category(uuid, category_name, vm_payload)



# Get VM details
# Define the payload
#payload = {
#    'kind': 'vm'
#}
#vm_uuid = "badb47e2-45f7-478e-86ca-996d9b8ccf2c"
#vm_details = connection.get_vm_details(vm_uuid,payload)
#print(f"VM Details: {vm_details}")


def main(argv):
    # Check if the required command-line arguments are provided
    pc_ip = "10.5.192.48"
    pc_username = "admin"
    pc_password = "Nutanix.123"
    sp_iter = 5
    vm_bacth = 5

    try:
        opts, args = getopt.getopt(argv,"hc:u:p:s:b:",["pc=","user=","passwd=","sp=","batch="])
    except getopt.GetoptError:
        print('storagepol.py -c <pc_ip> -u <user>  -p <passwd> -s <no of sp> -b <no vms in the batch>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('storagepol.py -c <pc_ip> -u <user>  -p <passwd> -s <no of sp> -b <no vms in the batch>')
            sys.exit()
        elif opt in ("-c", "--pc"):
            pc_ip = arg
        elif opt in ("-u", "--user"):
            pc_username = int(arg)
        elif opt in ("-p", "--passwd"):
            pc_password = int(arg)
        elif opt in ("-s", "--sp"):
            sp_inter = int(arg)
        elif opt in ("-b", "--batch"):
            vm_batch = int(arg)
        elif opt in ("-w", "--wait"):
            wait = int(arg)


    connection = NutanixConnection(pc_ip, pc_username, pc_password)
    
    # Generate the payloads
    #generate_payloads(cluster_ip, num_categories, num_policies)
    configure_category_sp(connection,vm_batch,sp_iter)
    sp_stress(connection,sp_iter)


if __name__ == '__main__':
    main(sys.argv[1:])

import sys,getopt
import random
import itertools
import json
import time
from utils import NutanixConnection
from collections import defaultdict

# Nutanix Prism Central details
#pc_ip = "10.5.16.147"


# Create a NutanixConnection object

def categories_list(connection):
    # Get categories
    # Define the payload
    catlist = []
    categoryl = (connection.get_categories_list())["entities"]
    #print (categoryl)
    for category in categoryl:
        if isinstance (category,dict) and "testSPCategory" in category["name"]:
            value = "c"+(category["name"]).split("testSPCategory")[1]
            catlist.append({"name":category["name"],"value":value})
            #print(category["name"],value)
    return catlist

def get_random_element(my_list):
    random.shuffle(my_list)
    return random.choice(my_list)

def sp_delete(connection):

    spolicyl = (connection.get_sp_list())["entities"]
    for stoagep in spolicyl:
        #print(stoagep["status"]["name"])
        if isinstance (stoagep,dict) and "testSpolicy" in stoagep["status"]["name"]:
        #if "testSpolicy" in stoagep["status"]["name"]:
            #spolicyl.extend({"name":stoagep["status"]["name"],"uuid":stoagep["metadata"]["uuid"]})
            connection.del_sp(stoagep["metadata"]["uuid"])

def sp_stress(connection):
    spolicyl = (connection.get_sp_list())["entities"]
    payload_list = []
    for stoagep in spolicyl:
        if isinstance (stoagep,dict) and "testSpolicy" in stoagep["status"]["name"]:
            #print(stoagep["status"]["name"],stoagep["metadata"]["uuid"],stoagep["metadata"])
            #print(stoagep["spec"]["resources"]["filter_list"][0]["scope_filter_expression_list"][0]["right_hand_side"]["categories"])
            #sys.exit()
            rand = (stoagep["status"]["name"])[len((stoagep["status"]["name"]).rstrip('0123456789')):]
            #category_name = "testSPCategory"+(stoagep["status"]["name"]).split("testSpolicy")[1]
            category_name = "testSPCategory"+str(rand)
            #value = "c"+(stoagep["status"]["name"]).split("testSpolicy")[1]
            value = "c"+str(rand)
            payload = connection.generate_sp_payload(stoagep["status"]["name"],category_name,value,"ALL",4,stoagep["metadata"]["spec_version"])
            #print(payload)
            payload_list.append({stoagep["metadata"]["uuid"]:payload})

    for pay in payload_list:
        for key in pay.keys():
            connection.update_policy(key,get_random_element(pay[key]))
            time.sleep(6)

def delete_category(connection):
    categoryl = categories_list(connection) 

    for cat in categoryl:
        print(cat["name"])
        resp = connection.del_category_value(cat)
        print (resp)
        resp = connection.del_category(cat["name"])
        print (resp)

def configure_category_sp(connection,batch_size,sp_iter):

    categoryl = categories_list(connection) 

    #for cat in categoryl:
    #    print(cat)
    #sys.exit()
    # Get VMs
    # Define the payload
    vg_payload = {
        'kind': 'volume_group',
        'offset': 0,
        'length': 1000
    }
    vm_payload = {
        'kind': 'vm',
        'offset': 0,
        'length': 1000
    }
    vms = (connection.get_vms(vm_payload))["entities"]
    #print(connection.get_vgs(vg_payload)) 
    time.sleep(120)
    vgs = (connection.get_vgs(vg_payload))["entities"]
    for vg in vgs:
        print(vg)
    res ={}
    # Split the list into batches of 10
    for vm,vg in zip(vms,vgs):
    #for vm in vms:
        res[vm["metadata"]["uuid"]] = vm["status"]["name"]
        res[vg["metadata"]["uuid"]] = vg["status"]["name"]

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
        if len(categoryl) < len(vm_batches): 
            rand = str(random.randint(100,128908))
            category_name = "testSPCategory"+str(rand)
            sp_name = "testSpolicy"+str(rand)
            value = "c"+str(rand)
            resp = connection.create_category(category_name)
            resp = connection.update_category_value(category_name,value)
            #categories = connection.get_category(category_name,payload)
        else:
            category = categoryl.pop()
            print(category)
            category_name = category["name"]
            rand = (category["value"])[len((category["value"]).rstrip('0123456789')):]
            sp_name = "testSpolicy"+str(rand)
            value = "c"+str(rand)

        resp = connection.create_strpol(sp_name,category_name,value)
        #print (categories)
        for key in vm_batch : 
            vm_payload['metadata']['categories'][category_name] = value
            vmspec = connection.get_vm(key)
            if vmspec != -1:
                print (key)
                vm_payload['metadata']['spec_version'] = vmspec['metadata']['spec_version']
                vm_payload['metadata']['categories_mapping'][category_name] = (res[key]).split()
                print("Add a vm to a category -> connection.add_vm_to_category")
                resp = connection.add_vm_to_category(key, category_name, vm_payload)
                print(resp)
        print(f"Sleep for 60 sec when task run for bacth -> {len(vm_batch)}")
        time.sleep(60)

def main(argv):
    # Check if the required command-line arguments are provided
    pc_ip = "10.5.192.48"
    pc_username = "admin"
    pc_password = "Nutanix.123"
    sp_iter = 5
    vm_batch = 5
    wait = 3600

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
    while 1:
        configure_category_sp(connection,vm_batch,sp_iter)
        time.sleep(60)
        sp_stress(connection)
        time.sleep(60)
        sp_delete(connection)
        time.sleep(wait)
        delete_category(connection)

if __name__ == '__main__':
    main(sys.argv[1:])

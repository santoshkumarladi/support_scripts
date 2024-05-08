import sys,getopt
import random
import itertools
import json
import ast
import time
from utils import NutanixConnection
from collections import defaultdict
from datetime import datetime, timedelta

# Nutanix Prism Central details
#pc_ip = "10.5.16.147"


# Create a NutanixConnection object

def totimestamp(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6


def categories_list(connection,pattern):
    # Get categories
    # Define the payload
    catlist = []
    cat = connection.get_categories_list(pattern)
    if cat :
        categoryl = (cat)["data"]
        for category in categoryl:
            if isinstance (category,dict) and pattern in category['fqName']:
                catlist.append({"name":category["fqName"], "value":category['name'], "extId":category['extId']})
    return catlist

def cluster_connected(connection):
    clslist = {}
    clusters = connection.get_clusters()
    clusters = clusters["entities"]
    for cluster in clusters:
        print(cluster["spec"]["resources"]["network"]["external_ip"],cluster['metadata']['uuid'],cluster['spec']['name'])
        clslist[cluster["spec"]["resources"]["network"]["external_ip"]] = {"uuid" : cluster['metadata']['uuid'] , "name" : cluster['spec']['name']}
    
    return clslist

def get_random_element(my_list):
    random.shuffle(my_list)
    return random.choice(my_list)


def delete_category(connection):
    categoryl = categories_list(connection,"testSPCategory") 

    for cat in categoryl:
        print(cat["name"])
        resp = connection.del_category_value(cat)
        print (resp)
        resp = connection.del_category(cat["name"])
        print (resp)

def configure_category_dr(connection,batch_size,src_uuid):

    vm_cat_attach_list = []
    categoryl = connection.get_categories_list("testSPCategory") 

    # Get VMs
    # Define the payload

    cluster = '(clusterReference=='+str(src_uuid["uuid"])+')'
    vg_payload = {
        'kind': 'volume_group',
        'offset': 0,
        'length': 1000,
        'filter' : cluster
    }
    cluster = '(cluster=='+str(src_uuid["uuid"])+')'
    print(cluster)
    vm_payload = {
        'kind': 'vm',
        'offset': 0,
        'length': 1000,
        'filter' : cluster
    }

    vms = (connection.get_vms(vm_payload))["entities"]
    time.sleep(120)
    page = 3
    vgs = (connection.get_vgs_per_cluster(src_uuid["uuid"],page,vg_payload))
    
    res ={}
    # Split the list into batches of 10
    for vm,vg in zip(vms,vgs):
    #for vm in vms:
        res[vm["metadata"]["uuid"]] =  {"name" : vm["status"]["name"], "type" : "vm"}
        res[vg["extId"]] =  {"name" : vg["name"], "type" : "vg"}

    resk = list(res.keys())
    #batch_size = 5
    vm_batches = [resk[i:i+batch_size] for i in range(0, len(res), batch_size)]

    print("\n****************************************\n")
    print(f"\n Details of PC - no of VM's {len(vms)} , no of categories {len(categoryl)} batch size {len(vm_batches)} no of VG's {len(vgs)}")
    print("\n****************************************\n")
    # Iterate over each batch and add the category
    #category_uuid = "your_category_uuid"
    for vm_batch in vm_batches:
        category = {}
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
        vg_payload = {
          "categories": [
                {
                "extId": "string",
                "entityType": "$UNKNOWN"
                }
            ]
        }

        if len(categoryl) < len(vm_batches): 
            print("\n****************************************\n")
            print(f"\nCreate New Category on the PC for Testing total categories {len(categoryl)} batch size {len(vm_batches)}")
            print("\n****************************************\n")

            rand = str(random.randint(100,128908))
            category_name = "testSPCategory"+str(rand)
            sp_name = "testSpolicy"+str(rand)
            value = "c"+str(rand)

            resp = connection.create_category(category_name)
            resp = connection.update_category_value(category_name,value)
            time.sleep(30)
            category = connection.get_category(category_name) 
            print(f"Details of created category --> {category}")
        else:
            category = categoryl.pop()
            print(f"Details of already created category --> {category}")
            category_name = category["name"]
            rand = (category["value"])[len((category["value"]).rstrip('0123456789')):]
            sp_name = "testSpolicy"+str(rand)
            value = category["value"]

        resp = connection.create_strpol(sp_name,category_name,value)
        for key in vm_batch :
            try:
                if  res[key]["type"] == "vm": 
                    vm_payload['metadata']['categories'][category_name] = value
                    vmspec = connection.get_vm(key)
                    if vmspec != -1:
                        print (key)
                        vm_payload['metadata']['spec_version'] = vmspec['metadata']['spec_version']
                        vm_payload['metadata']['categories_mapping'][category_name] = (res[key]["name"]).split()
                    
                        print(f"Add a vm to a category -> connection.add_vm_to_category {category_name} and {res[key]}")
                        resp = connection.add_vm_to_category(key, category_name, vm_payload)
                        print(resp)
                    print(f"Sleep for 60 sec when task run for bacth -> {len(vm_batch)}")
                    #vm_cat_attach_list.append({category_name : [value]})
                    time.sleep(60)
                else:
                    try:
                        vg_payload["categories"][0]["extId"] = category["extId"]
                        vg_payload["categories"][0]["entityType"] = "CATEGORY"
                        print(f"Add a vg to a category -> connection.add_vg_to_category {vg_payload}")
                        resp = connection.add_vg_to_category(key,vg_payload)
                        print(resp)
                        print(f"Sleep for 60 sec when task run for bacth -> {len(vm_batch)} and {res[key]}")
                        #vm_cat_attach_list[category_name] = [value]
                        time.sleep(60)
                    except TypeError as e:
                        # Catch the 'NoneType' object is not subscriptable error
                        print(f"Caught TypeError: {e}")
                        print("Continuing with the program...")
            except Exception as e:
                # Catch the 'NoneType' object is not subscriptable error
                print(f"Caught TypeError: {e}")
                print("Continuing with the program...")
        vm_cat_attach_list.append({category_name : [value]})
    return vm_cat_attach_list

def main(argv):
    # Check if the required command-line arguments are provided
    pc_ip = "10.5.192.48"
    pc_username = "admin"
    pc_password = "Nutanix.123"
    src_cls = ''
    dst_cls = ''
    nos = 3
    rpo_sec = 900
    vm_batch = 40
    wait = 3600
    rand = str(random.randint(100,128908))

    try:
        opts, args = getopt.getopt(argv,"hc:u:p:s:d:r:n:w",["pc=","user=","passwd=","src=","dst=","rpo=","nos=","wait="])
    except getopt.GetoptError:
        print('storagepol.py -c <pc_ip> -u <user>  -p <passwd> -s <src clsuter> -d <dst cluster> -r <rp in secs> -n <no of snapshots> -w <wait>  ')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('storagepol.py -c <pc_ip> -u <user>  -p <passwd> -s <src cluster> -d <dst cluster> -r <rp in secs> -n <no of snapshots> -w <wait>')
            sys.exit()
        elif opt in ("-c", "--pc"):
            pc_ip = arg
        elif opt in ("-u", "--user"):
            pc_username = int(arg)
        elif opt in ("-p", "--passwd"):
            pc_password = int(arg)
        elif opt in ("-s", "--src"):
            src_cls = arg
        elif opt in ("-d", "--dst"):
            dst_cls = arg
        elif opt in ("-r", "--rpo"):
            rpo_sec = int(arg)
        elif opt in ("-n", "--nos"):
            nos = int(arg)
        elif opt in ("-w", "--wait"):
            wait = int(arg)
    if src_cls == '':
        sys.exit()

    connection = NutanixConnection(pc_ip, pc_username, pc_password)
    pc_cls = cluster_connected(connection)
    src_uuid = pc_cls[src_cls]
    dst_uuid = pc_cls[dst_cls]
    pc_uuid = pc_cls[pc_ip]
    print (src_uuid['name'],src_uuid['uuid'],pc_uuid['uuid'])
    #cat_att_l = {}
    
    pd_name = 'testFITPD'+str(rand)
    cat_att_l = configure_category_dr(connection,vm_batch,src_uuid)
    #cat_att_l['testSPCategory100389'] = ['c100389'] 

    print(cat_att_l)
    for cat in cat_att_l:
        pd = pd_name+str(totimestamp(datetime.now()))
        connection.configure_dr(pd,pc_uuid["uuid"],src_uuid["uuid"],dst_uuid["uuid"],nos,rpo_sec,cat)


if __name__ == '__main__':
    main(sys.argv[1:])

import sys,getopt
import random
import itertools
import json
import ast
import time
from nutanixoperations import NutanixClusterOperations
from collections import defaultdict
from datetime import datetime, timedelta

# Nutanix Prism Central details
#pc_ip = "10.5.16.147"


# Create a NutanixConnection object

def totimestamp(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6


def get_random_elements(my_list,count):
    if len(my_list) < count:
        #raise ValueError("List must contain at least count elements.")
        print (f"List must contain at least {count} elements {my_list}.")
        return 0
    else :
        return random.sample(my_list, count)



def main(argv):
    # Check if the required command-line arguments are provided
    c_ip = ""
    c_username = "nutanix"
    c_password = "RDMCluster.123"
    nos = 3
    wait = 3600
    rand = str(random.randint(100,128908))
    ser_dict = {}
    
    try:
        opts, args = getopt.getopt(argv,"hc:u:p:n:w:",["cvm=","user=","passwd=","nos=","wait="])
    except getopt.GetoptError:
        print('killMultiService.py -c <cvm_ip> -u <user>  -p <passwd> -s <service/process list> -n <no of iterations> -w <wait>  ')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('killMultiService.py -c <cvm_ip> -u <user>  -p <passwd> -s <service/process list> -n <no of iterations> -w <wait>  ')
            sys.exit()
        elif opt in ("-c", "--cvm"):
            c_ip = arg
        elif opt in ("-u", "--user"):
            c_username = int(arg)
        elif opt in ("-p", "--passwd"):
            c_password = int(arg)
        elif opt in ("-n", "--nos"):
            nos = int(arg)
        elif opt in ("-w", "--wait"):
            wait = int(arg)
    if c_ip == '':
        sys.exit()

    j=0
    print(f"Wait -> {wait}")
    connection = NutanixClusterOperations(c_ip, c_username, c_password)
    
    svmips = connection.get_svm_ips()
    services = connection.get_services(svmips[0])
    for i in range(nos):
        ser_dict = connection.get_process(svmips,services,wait)
        #print(ser_dict)
        cvms = ser_dict.keys()
        if ser_dict[cvms[j]]:
            pids = []
            serv = get_random_elements(services,2)
            for sp in serv:
                print(f"kill {sp} process  ")
                if len(ser_dict[cvm][sp]) < 1:
                    cmd = " /usr/local/nutanix/cluster/bin/cluster start </dev/null>/dev/null 2>&1"
                    print("Restarting the cluster services ")
                    connection.run_cmd_remote(cmd,cvm)
                    #print("Get the pids again after services restart")
                    #ser_dict = connection.get_process(svmips,services,wait)
                    #print(f"New PIDs -> {ser_dict}")
                elements = get_random_elements(ser_dict[cvm][sp],2)
                if elements != 0 :
                    for pid in elements:
                        pids.append(pid)
                ser_dict[cvm].pop(sp)

            print(f"Killing pids {pids} of services -> {serv} on node -> {cvm}")
            connection.kill_service(cvm,pids)
            time.sleep(wait)
            cmd = " /usr/local/nutanix/cluster/bin/cluster start </dev/null>/dev/null 2>&1"
            print("Restarting the cluster services ")
            connection.run_cmd_remote(cmd,cvm)
            j = j+1 if j >= len(cvms)-1 else 0 
        

if __name__ == '__main__':
    main(sys.argv[1:])

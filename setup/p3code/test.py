ssh nutanix@10.46.33.12 "python3.6 -c \"
import psutil
import json
import os

def get_pids_by_name(process_name):
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name in proc.info['name']:
            pids.append(proc.info['pid'])

    cmd = f\\\"source /etc/profile; /usr/local/nutanix/cluster/bin/genesis status | grep -E {process_name}\\\"
    if len(pids) < 1:
        op = os.popen(cmd).read()
        pds = json.loads(op.split(':')[1].strip())
        for pid in pds:
            print(pid)
            pids.append(pid)

    return pids

def get_process_names_with_pids():
    process_dict = {}
    process_names = ['stargate', 'curator', 'zookeeper', 'placement_solver']
    for name in process_names:
        pids = get_pids_by_name(name)
        process_dict[name] = pids
    return process_dict

result_dict = get_process_names_with_pids()
print(json.dumps(result_dict))

"\"

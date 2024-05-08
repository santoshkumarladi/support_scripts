import requests
import urllib3
import json

# Disable SSL certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_clusters(pc_ip, pc_username, pc_password):
    # Request payload
    payload = {
        'kind': 'vm'
    }

    # Request headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Nutanix Prism Central API endpoint
    api_endpoint = f"https://{pc_ip}:9440/api/nutanix/v3/clusters/list"

    # Create a session
    session = requests.Session()
    session.auth = (pc_username, pc_password)
    session.verify = False  # Disable SSL verification (not recommended for production)

    print(f"API endpoint: {api_endpoint}")
    # Make a GET request to retrieve clusters
    response = session.post(api_endpoint, headers=headers, json=payload)

    # Check the response status code
    if response.status_code == 200:
        clusters_data = json.loads(response.text)
        clusters = clusters_data["entities"]
        for cluster in clusters:
            cluster_name = cluster["status"]["name"]
            cluster_uuid = cluster["metadata"]["uuid"]
            print(f"Cluster Name: {cluster_name}")
            print(f"Cluster UUID: {cluster_uuid}")
            print()
    else:
        print(f"Failed to retrieve clusters. Status code: {response.status_code}")
        print(f"Error message: {response.text}")


def get_vms(pc_ip, pc_username, pc_password):
    # Request payload
    payload = {
        'kind': 'vm'
    }

    # Request headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Nutanix Prism Central API endpoint
    api_endpoint = f"https://{pc_ip}:9440/api/nutanix/v3/vms/list"

    # Create a session
    session = requests.Session()
    session.auth = (pc_username, pc_password)
    session.verify = False  # Disable SSL verification (not recommended for production)

    print(f"API endpoint: {api_endpoint}")
    # Make a GET request to retrieve clusters
    response = session.post(api_endpoint, headers=headers, json=payload)

    # Check the response status code
    if response.status_code == 200:
        # Parse the response and extract VM details
        vm_list = response.json()['entities']
        for vm in vm_list:
            vm_name = vm['status']['name']
            vm_uuid = vm['metadata']['uuid']
            print(f"VM Name: {vm_name}\tVM UUID: {vm_uuid}")
    else:
        print(f"Failed to retrieve vms. Status code: {response.status_code}")
        print(f"Error message: {response.text}")

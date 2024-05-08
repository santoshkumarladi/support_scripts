import requests
import urllib3
import json
import itertools
import random

# Disable SSL certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NutanixConnection:
    def __init__(self, pc_ip, pc_username, pc_password, max_buffer_size=10485760):
        self.pc_ip = pc_ip
        self.pc_username = pc_username
        self.pc_password = pc_password
        self.max_buffer_size = max_buffer_size
        self.session = self._create_session()

    def _create_session(self):
        # Create a session
        session = requests.Session()
        session.auth = (self.pc_username, self.pc_password)
        session.verify = False  # Disable SSL verification (not recommended for production)
        session.timeout = (3, 380)  # Increase stream timeout to 60 seconds
        session.max_buffer_size = self.max_buffer_size
        return session
        #def _make_request(self, api_endpoint, payload=None):
    def _make_request(self, api_endpoint, payload=None , method='POST'):
        try :
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            method = str(method).upper()
            if method not in ('GET', 'POST', 'PUT', 'DELETE'):
                raise ValueError(f"Invalid HTTP method: {method}")

            #response = self.session.post(api_endpoint, headers=headers, json=payload)
            print(api_endpoint)
            print()
            response = self.session.request(method, api_endpoint, headers=headers, json=payload, stream=True)
            response.raise_for_status()  # Raise an exception for non-2xx status codes

            print(response)
            response_content = b""
            for chunk in response.iter_content(chunk_size=None):
                response_content += chunk

            return json.loads(response_content.decode())
            if response.status_code == 200 or response.status_code == 202:
                return json.loads(response_content.decode())
        except requests.exceptions.RequestException as e:
            print("Error occurred during the API request:", e)
            return -1
        except (KeyError, ValueError) as e:
            print("Error occurred while parsing the JSON response:", e)
            return -1

    def get_clusters(self):
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/clusters/list"
        payload = {
          "kind": "cluster"
        }
        return self._make_request(api_endpoint, payload, method='POST')

    def get_vgs(self, payload=None):
        print(payload)
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/volume_groups/list"
        return self._make_request(api_endpoint, payload, method='POST')

    def get_vgs_per_cluster(self, src_uuid, pages=4, payload=None):
        vglist = []
        print(payload)
        for i in range (pages):
            #api_endpoint = f"https://{self.pc_ip}:9440/api/volumes/v4.0.b1/config/volume-groups?$page=0&$limit=100"
            api_endpoint = f"https://{self.pc_ip}:9440/api/volumes/v4.0.b1/config/volume-groups?%24page={i}&%24limit=100"
            vgs = self._make_request(api_endpoint, payload, method='GET')
            if  "data" in vgs:
                vgs = vgs["data"]
                for vg in vgs:
                    #'usageType': 'INTERNAL'
                    #if isinstance (vg,dict) and "usageType" not in vg:
                    if isinstance (vg,dict) and vg["clusterReference"] == src_uuid and "usageType" not in vg:
                        vglist.append({"name": vg['name'] , "extId": vg['extId']})
                        #print( vg['name'],vg['extId'],vg['clusterReference'])
        return vglist

    def get_vms(self, payload=None):
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/vms/list"
        return self._make_request(api_endpoint, payload, method='POST')

    def get_vms_per_cluster(self, cluster_uuid,payload=None):
        payload = {
            "filter": f"cluster_uuid=={cluster_uuid}"
        }
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/vms/list"
        return self._make_request(api_endpoint, payload, method='POST')

    def get_vm(self, uuid ,payload=None):
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/vms/{uuid}"
        return self._make_request(api_endpoint, payload, method='GET')

    def get_vg(self, uuid ,payload=None):
        #api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/volume_groups/{uuid}"
        api_endpoint = f"https://{self.pc_ip}:9440/api/volumes/v4.0.b1/config/volume-groups/{uuid}"
        return self._make_request(api_endpoint, payload, method='GET')

    def get_categories_v3_list(self, payload=None):
        payload = {
            "length": 10000,
            "offset": 0
        }
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/categories/list"
        return self._make_request(api_endpoint, payload, method='POST')

    def get_categories_list_a1(self, payload=None):
        api_endpoint = f"https://{self.pc_ip}:9440/api/prism/v4.0.a1/config/categories?$page=0&$limit=100"
        return self._make_request(api_endpoint, payload, method='GET')

    def get_categories_list(self, category_name, pages=3, payload=None):
        cats = []
        for i in range (pages):
            api_endpoint = f"https://{self.pc_ip}:9440/api/prism/v4.0.a2/config/categories?%24page={i}&%24limit=100"
            categories = self._make_request(api_endpoint, payload, method='GET')
            if  "data" in categories:
                categories = categories["data"]
                for cat in categories:
                    if isinstance (cat,dict) and category_name in cat['key']:
                        cats.append({"name": cat['key'] , "extId": cat['extId'], "value":cat['value']})
                        #print( cat['key'],cat['extId'],cat['value'])
        return cats

    def get_sp_list(self, payload=None):
        payload = {
            "length": 10000,
            "offset": 0
        }
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/storage_policies/list"
        return self._make_request(api_endpoint, payload, method='POST')

    def del_sp(self, uuid, payload=None):
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/storage_policies/{uuid}"
        return self._make_request(api_endpoint, payload, method='DELETE')

    def del_category_value(self, category_name, payload=None):
        name = category_name["name"]
        value = category_name["value"]
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/categories/{name}/{value}"
        return self._make_request(api_endpoint, payload, method='DELETE')

    def del_category(self, category_name, payload=None):
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/categories/{category_name}"
        return self._make_request(api_endpoint, payload, method='DELETE')

    def get_category(self, category_name, pages=3, payload=None):
        for i in range (pages):
            api_endpoint = f"https://{self.pc_ip}:9440/api/prism/v4.0.a2/config/categories?%24page={i}&%24limit=100"
            categories = self._make_request(api_endpoint, payload, method='GET')
            if  "data" in categories:
                categories = categories["data"]
                for cat in categories:
                    if isinstance (cat,dict) and category_name == cat['key']:
                        return {"name": cat['key'] , "extId": cat['extId'], "value":cat['value']} 
        return None

    def create_category(self, category_name):
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/categories/{category_name}"
        payload = {
                    "description": "string",
                    "name": category_name
        }
        return self._make_request(api_endpoint, method='PUT', payload=payload)

    def enable_protection(self, uuid):
        api_endpoint = f"https://{self.pc_ip}:9440/api/clustermgmt/v4.0.b1/config/clusters/{uuid}/$actions/protect"
        payload = {
          "kind": "cluster",
          "sort_attribute": "string",
          "length": 1,
          "sort_order": "string",
          "offset": 0
        }
        #payload = {
        #  "localSnapshotRetentionPolicy": 2,
        #  "remoteSnapshotRetentionPolicy": 4,
        #  "protectionRpoInMinutes": 240,
        #}
         #"protectionTarget": "LOCAL"
        return self._make_request(api_endpoint, method='POST', payload=payload)

    def disable_protection(self, uuid, payload=None):
        api_endpoint = f"https://{self.pc_ip}:9440/api/clustermgmt/v4.0.b1/config/clusters/{uuid}/$actions/unprotect"
        return self._make_request(api_endpoint, method='POST', payload=payload)

    def protection_status(self, uuid, payload=None):
        api_endpoint = f"https://{self.pc_ip}:9440/api/clustermgmt/v4.0.b1/config/clusters/{uuid}/protection-info"
        payload = {
          'kind': 'protection-info',
          'offset': 0,
          'length': 1000
        }
        return self._make_request(api_endpoint, method='GET', payload=payload)

    def recovery_info(self, uuid, payload=None):
        api_endpoint = f"https://{self.pc_ip}:9440/api/clustermgmt/v4.0.b1/config/clusters/{uuid}/recovery-info"
        payload = {
          'kind': 'recovery-info',
          'offset': 0,
          'length': 1000
        }
        return self._make_request(api_endpoint, method='GET', payload=payload)

    def create_strpol(self, pol_name,category_name,value):
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/storage_policies"
        payload = {
            "spec": {
                "name": pol_name,
                "resources": {
                    "encryption": {
                        "state": "ENABLE"
                    },
                    "fault_tolerance": {
                        "replication_factor": 2
                    },
                    "compression": {
                        "state": "ENABLE",
                        "inline_compression": True
                    },
                    "filter_list": [
                    {
                        "entity_filter_expression_list": [
                        {
                            "operator": "IN",
                            "right_hand_side": {
                                "collection": "ALL"
                            },
                            "left_hand_side": {
                            "entity_type": "VM"
                            }
                        }
                        ],
                      "scope_filter_expression_list": [
                      {
                        "operator": "IN",
                        "right_hand_side": {
                            "categories": {
                              category_name: [
                                value
                              ]
                            }
                        },
                          "left_hand_side": "CATEGORY"
                        }
                        ]
                    }
                    ]
                },
        "description": "This is a test storage policy"
        },
          "metadata": {
            "kind": "storage_policy"
            }
        }
        print(payload)
        return self._make_request(api_endpoint, method='POST', payload=payload)

    def update_category_value(self, categories, value):
        payload = {
            "value": value
        }
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/categories/{categories}/{value}"
        return self._make_request(api_endpoint, method='PUT', payload=payload)

    def update_policy(self, uuid, payload):
        print(payload)
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/storage_policies/{uuid}"
        return self._make_request(api_endpoint, method='PUT', payload=payload)

    def add_vm_to_category(self, vm_uuid, category_uuid, payload):
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/mh_vms/{vm_uuid}"
        return self._make_request(api_endpoint, method='PUT', payload=payload)

    def add_vg_to_category(self, vg_uuid, payload):
        #https://{pc-ip}:9440/api/volumes/v4.0.b1/config/volume-groups/{extId}/$actions/associate-category
        api_endpoint = f"https://{self.pc_ip}:9440/api/volumes/v4.0.b1/config/volume-groups/{vg_uuid}/$actions/associate-category"
        return self._make_request(api_endpoint, method='POST', payload=payload)

    def batch_add_vm_to_category(self, vm_uuids, category_uuid):
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/vms"
        payload = {
            'spec': {
               'resources': []
            }
        }

        for vm_uuid in vm_uuids:
            payload['spec']['resources'].append({
                'uuid': vm_uuid,
                'categories': [
                    {
                        'kind': 'category',
                        'uuid': category_uuid
                    }
                ]
            })

        response = self.session.put(api_endpoint, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Request failed with status code: {response.status_code}\nError message: {response.text}")

        return response.json()

    def generate_sp_payload(self, pol_name,category_name,value,entity_type,num_policies,spec_version):

        payload_list = []
        # Define possible values for each payload key
        encryption_state_values = ['ENABLE', 'DISABLE']
        replication_factor_values = [2, 3, 2, 3]
        qos_policy_values = [-1, 10000]
        compression_state_values = ['ENABLE', 'DISABLE']
        inline_compression_values = [True, False]

        # Generate all combinations of payload values
        combinations = list(itertools.product(encryption_state_values, replication_factor_values,
                                          compression_state_values, inline_compression_values,qos_policy_values
                                          ))

        # Iterate over the combinations and limit to the desired number of policies
        num_policies = min(num_policies, len(combinations))
        selected_combinations = combinations[:num_policies]

        # Iterate over the selected combinations
        for combo in selected_combinations:
            encryption_state, replication_factor, compression_state, inline_compression,qos \
            = combo
            if 'DISABLE' in compression_state:
                inline_compression_values = False

            # Create the payload dictionary for the combination
            payload = {
                "spec": {
                    "name": pol_name,
                    "resources": {
                        "qos": {
                            "throttled_iops": qos
                        },
                        "encryption": {
                            "state": encryption_state
                        },
                        "fault_tolerance": {
                            "replication_factor": replication_factor
                        },
                        "compression": {
                            "state": compression_state,
                            "inline_compression": inline_compression
                        },
                        "filter_list": [
                        {
                            "entity_filter_expression_list": [
                                {
                                    "operator": "IN",
                                    "right_hand_side": {
                                        "collection": "ALL"
                                    },
                                    "left_hand_side": {
                                    "entity_type": "VM"
                                    }
                                }
                            ],
                            "scope_filter_expression_list": [
                                {
                                    "operator": "IN",
                                    "right_hand_side": {
                                        "categories": {
                                          category_name: [
                                            value
                                          ]
                                        }
                                    },
                                    "left_hand_side": "CATEGORY"
                                }
                            ]
                        }
                        ]
                    },
                },
                "metadata": {
                    "kind": "storage_policy", 
                    "spec_version": spec_version
                }
            }
        
            # Convert payload dictionary to JSON string
            payload_json = json.dumps(payload)
            #print(payload_json)
            payload_list.append(payload) 
            #print()
        return payload_list
            
#get_vm_details(self, vm_uuid, payload=None):
        #api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/vms/{vm_uuid}"
        #print (api_endpoint)
        #return self._make_request(api_endpoint, method='POST')

    def configure_dr(self, pol_name,pc_uuid,src_uuid,dst_uuid,nosnap,rpo,cat_name):

        payload = {
            "spec": {
                "resources": {
                    "category_filter": {
                        "type": "CATEGORIES_MATCH_ANY",
                        "params": cat_name
                    },
                    "availability_zone_connectivity_list": [
                        {
                            "destination_availability_zone_index": 1,
                            "source_availability_zone_index": 0,
                            "snapshot_schedule_list": [
                                {
                                    "recovery_point_objective_secs": rpo,
                                    "local_snapshot_retention_policy": {
                                        "num_snapshots": nosnap
                                    },
                                    "remote_snapshot_retention_policy": {
                                        "num_snapshots": nosnap
                                    }
                                }
                            ]
                        },
                        {
                            "destination_availability_zone_index": 0,
                            "source_availability_zone_index": 1,
                            "snapshot_schedule_list": [
                                {
                                    "recovery_point_objective_secs": rpo,
                                    "local_snapshot_retention_policy": {
                                        "num_snapshots": nosnap
                                    },
                                    "remote_snapshot_retention_policy": {
                                        "num_snapshots": nosnap
                                    }
                                }
                            ]
                        }
                    ],
                    "ordered_availability_zone_list": [
                        {
                            "cluster_uuid": src_uuid,
                            "availability_zone_url": pc_uuid
                        },
                        {
                            "cluster_uuid": dst_uuid,
                            "availability_zone_url": pc_uuid
                        }
                    ],
                    "primary_location_list": [
                        0
                    ]
                },
                "name": pol_name 
            },
            "metadata": {
                "kind": "protection_rule"
            }
        }
        #jpayload = json.dumps(payload)
        #json_payload_single_quotes = jpayload.replace('"',"'")
        print(payload)
        api_endpoint = f"https://{self.pc_ip}:9440/api/nutanix/v3/protection_rules"
        return self._make_request(api_endpoint, method='POST', payload=payload)

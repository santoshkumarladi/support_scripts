import requests
import json
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

# Set the base URL for the Nutanix REST API
base_url = "https://10.40.176.27:9440/api/nutanix/v3/storage_policies/list"

# Set the headers for the REST API call
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Set the credentials for the REST API call
credentials = ('admin', 'Nutanix.123')

payload = {
    "length": 10,
    "offset": 0
}
# Define the storage policy
policy = {
    "spec": {
        "name": "Sample Storage Policy",
        "description": "This is a sample storage policy",
        "resources": {
            "replica_count": 2
        }
    }
}

# Make the REST API call to create the storage policy
response = requests.post(base_url , auth=credentials, headers=headers, data=json.dumps(payload))

# Check the response status code
if response.status_code == 201:
    print("Storage policy created successfully")
else:
    print("Failed to create storage policy")
    print(response.text)

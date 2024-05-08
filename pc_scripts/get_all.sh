#!/bin/bash

# Nutanix Prism Central details
pc_ip="10.5.192.48"
pc_username="admin"
pc_password="Nutanix.123"

# API endpoint URLs
clusters_endpoint="https://${pc_ip}:9440/api/nutanix/v3/clusters/list"
vms_endpoint="https://${pc_ip}:9440/api/nutanix/v3/vms/list"
categories_endpoint="https://${pc_ip}:9440/api/nutanix/v3/categories/list"
create_category_endpoint="https://${pc_ip}:9440/api/nutanix/v3/categories"
add_vm_to_category_endpoint="https://${pc_ip}:9440/api/nutanix/v3/vms/VM_UUID"

# Request headers
headers="Content-Type: application/json"
auth_header="Authorization: Basic $(echo -n "${pc_username}:${pc_password}" | base64)"

# Get clusters
clusters_response=$(curl -s -k -X POST -H "${headers}" -H "${auth_header}" "${clusters_endpoint}")
clusters=$(echo "${clusters_response}" | jq -r '.entities[] | .status.name, .metadata.uuid')

# Print clusters
echo "Clusters:"
while read -r cluster_name && read -r cluster_uuid; do
    echo "Cluster Name: ${cluster_name}"
    echo "Cluster UUID: ${cluster_uuid}"
    echo
done <<< "${clusters}"

# Get VMs
vms_response=$(curl -s -k -X POST -H "${headers}" -H "${auth_header}" "${vms_endpoint}")
vms=$(echo "${vms_response}" | jq -r '.entities[] | .status.name, .metadata.uuid')

# Print VMs
echo "VMs:"
while read -r vm_name && read -r vm_uuid; do
    echo "VM Name: ${vm_name}"
    echo "VM UUID: ${vm_uuid}"
    echo
done <<< "${vms}"

# Get categories
categories_response=$(curl -s -k -X POST -H "${headers}" -H "${auth_header}" "${categories_endpoint}")
categories=$(echo "${categories_response}" | jq -r '.entities[] | .metadata.kind, .metadata.uuid')

# Print categories
echo "Categories:"
while read -r category_kind && read -r category_uuid; do
    echo "Category Kind: ${category_kind}"
    echo "Category UUID: ${category_uuid}"
    echo
done <<< "${categories}"

# Create category
new_category_name="NewCategory"
create_category_payload=$(jq -n --arg name "${new_category_name}" '{"api_version": "3.1", "metadata": {"kind": "category", "name": $name}}')
create_category_response=$(curl -s -k -X POST -H "${headers}" -H "${auth_header}" -d "${create_category_payload}" "${create_category_endpoint}")
new_category_uuid=$(echo "${create_category_response}" | jq -r '.metadata.uuid')

echo "New Category created:"
echo "Category Name: ${new_category_name}"
echo "Category UUID: ${new_category_uuid}"
echo

# Add VM to category
vm_uuid="your_vm_uuid"
add_vm_to_category_payload=$(jq -n --arg uuid "${new_category_uuid}" '[{"kind": "category", "uuid": $uuid}]')
add_vm_to_category_endpoint="${add_vm_to_category_endpoint/VM_UUID/$vm_uuid}"
add_vm_to_category_response=$(curl -s -k -X PUT -H "${headers}" -H "${auth_header}" -d "${add_vm_to_category_payload}" "${add_vm_to_category_endpoint}")

echo "VM added to Category:"
echo "VM UUID: ${vm_uuid}"
echo "Category UUID: ${new_category_uuid}"


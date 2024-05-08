#! /bin/bash

$log_path=$1
dmesg > $logp_path"/dmesg_$(date +"%Y_%m_%d_%I_%M_%p").log" 

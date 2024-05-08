#! /bin/bash

#set -x
sudo zgrep "^F01*" /mnt/archive/binary-logs/bluebell/*/home/nutanix/data/logs/st*.FATAL.*
sudo zgrep "^F01*" /mnt/archive/binary-logs/bluebell/*/home/nutanix/data/logs/cu*.FATAL.*
sudo zgrep "^F01*" /mnt/archive/binary-logs/bluebell/*/home/nutanix/data/logs/cer*.FATAL.*

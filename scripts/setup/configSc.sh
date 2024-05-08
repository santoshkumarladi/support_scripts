#! /bin/bash

set -x
mountp=$1
echo " wget -r -np -nH --reject '*.html*' http://10.41.70.50/scavenger/ -P ./"
` wget -r -np -nH --reject '*.html*' http://10.41.70.50/scavenger/ -P ./`
echo "chmod 777 /home/nutanix/scavenger/setuparchive.sh"
chmod 777 /home/nutanix/scavenger/setuparchive.sh
echo "~/scavenger/setuparchive.sh $mountp"
/home/nutanix/scavenger/setuparchive.sh $mountp

sleep 1

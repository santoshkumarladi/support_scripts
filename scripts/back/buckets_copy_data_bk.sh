#!/bin/sh
set -x
SRC="/mnt/logs"
#SRC="/var/www/html/TEST_LOGS"
DST="/var/www/html/s3_nas_test1"
#LOCALMNT2="/mnt/afssv3"
#echo "-----------------------------------------------------"
#echo "-----------------------------------------------------"
#echo "-----------------------------------------------------" 
for i in $SRC/*;
do
#cp -a "$i" "$DST/" 
cp -a "$i" "$DST/" &
#sleep 60
#sudo nice -n -10 cp -a "$i" "$DST/"
done

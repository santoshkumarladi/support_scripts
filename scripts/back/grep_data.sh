#!/bin/sh
set -x
SRC="/mnt/logs"
#SRC="/var/www/html/TEST_LOGS"
#DST="/var/www/html/s3_nas_test1"
#LOCALMNT2="/mnt/afssv3"
#echo "-----------------------------------------------------"
#echo "-----------------------------------------------------"
#echo "-----------------------------------------------------" 
#for i in $SRC/*;
#do
#cp -a "$i" "$DST/" 
#day=`date`
#TODAY=$(date)
day=`date +"%T"`
echo "Date: $day" 
echo "-----------------------------------------------------"
echo "-----------------------------------------------------"
echo "-----------------------------------------------------" 


for i in {1..9}
do
sudo grep -r error /mnt/logs/011019-040823_44A3E8* &
sudo grep -r vdisk /mnt/logs/011019-040823_44A3E8* &
sudo grep -r NFS /mnt/logs/011019-040823_44A3E8* &
sudo grep -r checksum /mnt/logs/011019-040823_44A3E8* &
sudo grep -r egroup /mnt/logs/011019-040823_44A3E8* &
sudo grep -r map /mnt/logs/011019-040823_44A3E8* &
sudo grep -r  /mnt/logs/011019-040823_44A3E8* &
sudo ls -ltrR /mnt/logs &
sudo ls -ltrR /mnt/logs &
sudo ls -ltrR /mnt/logs &
sudo ls -ltrR /mnt/logs &
sudo ls -ltrR /mnt/logs &

done
#sleep 60
#sudo nice -n -10 cp -a "$i" "$DST/"
#done

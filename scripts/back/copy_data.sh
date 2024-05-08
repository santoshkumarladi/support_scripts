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
cp -a $SRC/011019-040823_44A3E8 $SRC/011019-040823_44A3E8_$i$day &
done
#sleep 60
#sudo nice -n -10 cp -a "$i" "$DST/"
#done

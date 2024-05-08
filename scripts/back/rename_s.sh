#!/bin/sh
set -x
LOCALMNT1="/mnt/afss"
#LOCALMNT2="/mnt/afssv3"
echo "-----------------------------------------------------"
echo "-----------------------------------------------------"
echo "-----------------------------------------------------" 

sudo mkdir -p $LOCALMNT1
#sudo mkdir -p $LOCALMNT2
sudo mount 10.40.231.199:/volume1 $LOCALMNT1
#sudo mount 10.5.71.180:/volume3 $LOCALMNT2
sudo /usr/bin/find $LOCALMNT1 -maxdepth 1 -type d -not -path "/mnt/afss/corr*" -not -path "/mnt/afss/eggs_DONT_DELETE" -mtime +10 -exec sudo mv {} {}_del \;
#sudo /usr/bin/find $LOCALMNT2 -maxdepth 1 -type d -not -path "/mnt/afsf/corruptions" -not -path "/mnt/afsf/eggs_DONT_DELETE" -mtime +15 -exec sudo mv {} {}_del \;
sudo rm -rf  $LOCALMNT1/*_del/*
sudo rm -rf  $LOCALMNT1/*_del/*
sudo umount $LOCALMNT1/*_del
sudo umount $LOCALMNT1/*_del
#sudo rm -rf  $LOCALMNT2/*_del/*
#sudo rm -rf  $LOCALMNT2/*_del/*
#sudo umount $LOCALMNT2/*_del
#sudo umount $LOCALMNT2/*_del
#sudo /usr/bin/find $LOCALMNT1 -maxdepth 1 -type d -mtime +30 -exec sudo umount {}  \;
sudo rmdir $LOCALMNT1/*_del
sudo rmdir $LOCALMNT1/*_del
sudo umount $LOCALMNT1
sudo umount $LOCALMNT1
#sudo rmdir $LOCALMNT2/*_del
#sudo rmdir $LOCALMNT2/*_del
#sudo umount $LOCALMNT2
#sudo umount $LOCALMNT2

day=`date`
#TODAY=$(date)
echo "Date: $day" 
echo "-----------------------------------------------------"
echo "-----------------------------------------------------"
echo "-----------------------------------------------------" 


echo "$1----------------------------------------------------------------------"
#x=`ls -tl /var/www/html/NAS_LOGS/bigint_21012020/$1/home/nutanix/data/logs/sysstats/iostat.INFO* | head -n 1 | cut -d' '  -f 9`
x=`ls -tl /var/www/html/NAS_LOGS/bigint_25022020/$1/home/nutanix/data/logs/sysstats/iostat.INFO* | head -n 1 | cut -d' '  -f 9`
echo $x
#grep -n "02\/22\/2020 02:24:" $x | grep "PM" > /tmp/1
zgrep -n "02\/25\/2020 02:14:" $x | grep "PM" > /tmp/1
line=`head -n 1 /tmp/1 | cut -d':' -f 1`
echo $line
head -n $line $x | tail -n 100

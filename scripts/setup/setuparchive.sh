set -x
mountp=$1
for ip in `svmips`; do echo $ip; scp -r /tmp/nfs-utils nutanix@$ip:/tmp ; done
for ip in `svmips`; do echo $ip; ssh -q $ip "source /etc/profile; sudo yum localinstall --nogpgcheck -y /tmp/nfs-utils/*";done;
for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mkdir /mnt/archive; sudo mount $mountp /mnt/archive/";done;
for ip in `svmips`; do echo $ip; ssh -q $ip 'crontab -l >> /tmp/crontab_$(date '+%m%d%Y').txt';done;
for ip in `svmips`; do echo $ip; ssh -q $ip '(/usr/bin/crontab -l && echo "# Keep the archive log dir mounted after reboot ") | /usr/bin/crontab -';done;
for ip in `svmips`; do echo $ip; ssh -q $ip "(/usr/bin/crontab -l && echo \"@reboot sudo mount $mountp /mnt/archive  >/dev/null 2>&1\") | /usr/bin/crontab - ";done;
#cmd="@reboot sudo mount $mountp"
#echo "(/usr/bin/crontab -l && echo \"@reboot sudo mount $mountp /mnt/archive  >/dev/null 2>&1 \") | /usr/bin/crontab -"

sleep 1

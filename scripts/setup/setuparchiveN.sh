#! /bin/bash

set -x
mountp=$1
echo " wget -r -np -nH --reject '*.html*' http://10.41.70.50/scavenger/ -P ./"
` wget -r -np -nH --reject '*.html*' http://10.41.70.50/scavenger/ -P ./`
for ip in `svmips`; do echo $ip; ssh -q $ip USE_SAFE_RM=no rm -rf ~/config/scavenger.gflags* ; done
for ip in `svmips`; do echo $ip; scp -r ~/scavenger/scavenger.gflags nutanix@$ip:~/config ; done
for ip in `svmips`; do echo $ip; scp -r ~/scavenger/nfs-utils nutanix@$ip:/tmp ; done
echo "sudo mv  ~/scavenger/scavengerSetup.service /etc/systemd/system/"
`sudo mv  ~/scavenger/scavengerSetup.service /etc/systemd/system/`
if [ -e /etc/systemd/system/scavengerSetup.service ]
then
    for ip in `svmips`; do echo $ip; ssh -q $ip "source /etc/profile; sudo yum localinstall --nogpgcheck -y /tmp/nfs-utils/*";done;
    for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mkdir /mnt/archive ";done;
    for ip in `svmips`; do echo $ip; ssh -q $ip "sudo mount  $mountp /mnt/archive/";done;
    for ip in `svmips`; do echo $ip; ssh -q $ip "sudo echo $mountp /mnt/archive/ nfs4 defaults 0 0 | sudo tee -a /etc/fstab > /dev/null  ";done;
    for ip in `svmips`; do echo $ip; ssh -q $ip 'crontab -l >> /tmp/crontab_$(date '+%m%d%Y').txt';done;
    for ip in `svmips`; do echo $ip; ssh -q $ip '(/usr/bin/crontab -l && echo "# Keep the archive log dir mounted after reboot ") | /usr/bin/crontab -';done;
    for ip in `svmips`; do echo $ip; ssh -q $ip "(/usr/bin/crontab -l && echo \"@reboot setup 90 ;sudo mount $mountp /mnt/archive  >/dev/null 2>&1\") | /usr/bin/crontab - ";done;
    for ip in `svmips`; do echo $ip; ssh -q $ip "(/usr/local/nutanix/cluster/bin/genesis stop scavenger ; /usr/local/nutanix/cluster/bin/cluster start)";done;
    sleep 30
    echo "sudo systemctl daemon-reload"
    `sudo systemctl daemon-reload`
    echo "sudo systemctl enable scavengerSetup.service"
    `sudo systemctl enable scavengerSetup.service`
    echo "sudo systemctl start scavengerSetup.service"
    `sudo systemctl start scavengerSetup.service`
    echo "/usr/local/nutanix/cluster/bin/cluster restart_genesis"
    `/usr/local/nutanix/cluster/bin/cluster restart_genesis`
    echo "/usr/local/nutanix/cluster/bin/cluster start"
    `/usr/local/nutanix/cluster/bin/cluster start`
    echo "Setup deamon is done"
else
    echo "file is not exists"
fi

sleep 1

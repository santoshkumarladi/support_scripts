#! /bin/bash

set -x
#sleep 120
sudo mount -o vers=3 filesv2.cdp.nutanix.com:/manual_logs /var/www/html/manual_logs
sudo mount -o vers=3 filesv2.cdp.nutanix.com:/NAS_logs /var/www/html/NAS_LOGS
sudo mount -o vers=3 filesv1.cdp.nutanix.com:/volume1 /var/www/html/TEST_LOGS
#sudo mount 10.40.231.204:/volume1 -o vers=3 /var/www/html/TEST_LOGS
#sudo mount 10.40.167.227:/volume2 -o vers=3 /var/www/html/JIRA_LOGS
#sudo mount 10.40.167.231:/volume4 -o vers=3 /var/www/html/g_v4
#sudo mount 10.40.167.231:/volume5 -o vers=3 /var/www/html/g_v5
#sudo mount -o vers=3 10.40.231.203:/volume3/coverage_builds /var/www/html/coverage_builds
#sudo mount 10.40.231.228:/volume1 -o vers=3 /mnt/logs
#s3fs nas.logs1 /var/www/html/s3_nas_logs -o passwd_file=/home/nutanix/.passwd-s3fs -o url="http://10.40.165.69" -o use_path_request_style
#s3fs nas.logs1 /var/www/html/s3_nas_logs -o url=http://10.40.165.69:7200 -o use_path_request_style -o enable_noobj_cache -o allow_other -o notsup_compat_dir
#s3fs nas.logs1 /var/www/html/s3_nas_logs -o url=http://10.40.165.69:7200 –o passwd_file=/home/nutanix/.passwd-s3fs -o cipher_suites=AESGCM -o kernel_cache -o max_stat_cache_size=100000 -o multipart_size=52 -o parallel_count=30 -o multireq_max=30 -o max_background=1000 -o dbglevel=warn -o sigv2
#s3fs nas.logs1 /var/www/html/s3_nas_logs -o passwd_file=/home/nutanix/.passwd-s3fs -o url=http://10.40.165.69:7200 -o cipher_suites=AESGCM -o max_stat_cache_size=100000 -o multipart_size=52 -o parallel_count=30 -o multireq_max=30 -o max_background=1000 -o dbglevel=warn -o sigv2
#s3fs nas.test /var/www/html/s3_nas_logs -o passwd_file=/home/nutanix/.passwd-s3fs -o url="http://10.45.16.251" -o use_path_request_style -o umask=0022,uid=1000,gid=1000,mp_umask=0022,allow_other
#s3fs nas.test /var/www/html/s3_nas_test1 -o passwd_file=/home/nutanix/.passwd-s3fs -o url="http://10.45.28.125" -o use_path_request_style -o umask=0022,uid=1000,gid=1000,mp_umask=0022,allow_other

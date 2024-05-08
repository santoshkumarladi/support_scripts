#!/bin/bash

# Change permissions for /mnt/archive/ and /mnt/archive/laarchive/
sudo chmod 777 /mnt/archive/
while true
do

    if [ -e /mnt/archive/laarchive ]
    then
        #echo "$(date +"%Y-%m-%d %H:%M:%S") - Changing permissions for /mnt/archive/laarchive/"
        #sudo chmod 777 /mnt/archive/laarchive
        # Check if /mnt/archive/laarchive was created more than 24 hours ago
        last_modified_time=$(stat -c %Y /mnt/archive/laarchive)
        current_time=$(date +%s)
        time_difference=$((current_time - last_modified_time))

        if [ "$time_difference" -ge 86300 ]
        then
            current_date=$(date +%Y-%m-%d)
            current_date_time=$(date +%Y-%m-%d-%H%M%S)

            echo "$(date +"%Y-%m-%d %H:%M:%S") - Checking for directories with the same date pattern: Previous-logs-$current_date*"
            same_name_existing_dirs=$(find /mnt/archive -maxdepth 1 -type d -name "Previous-logs-$current_date*")
            if [ -z "$same_name_existing_dirs" ]
            then
                echo "$(date +"%Y-%m-%d %H:%M:%S") - No directories found with the same date pattern for today."

                # Flag to check if any recent directory is found
                recent_dir_found=0

                echo "$(date +"%Y-%m-%d %H:%M:%S") - Checking for existing directories with name pattern: Previous-logs-*"
                # Generate a random sleep time between 0 and 600 seconds (10 minutes)
                #random_sleep=$(( RANDOM % 600 ))
                random_sleep=6
                echo "Sleeping for $random_sleep seconds before starting the main loop..."
                sleep "$random_sleep"
                # Find directories with name starting with "Previous-logs-"
                existing_dirs=$(find /mnt/archive -maxdepth 1 -type d -name "Previous-logs-*")
                # Loop through each directory
                for dir in $existing_dirs
                do
                    dir_name=$(basename "$dir")
                    dir_creation_time=$(stat -c %Y "$dir")

                    # Check if the directory was created less than 2 hours ago
                    time_since_creation=$((current_time - dir_creation_time))
                    if [ "$time_since_creation" -lt 7200 ]
                    then
                        # If a recent directory is found, set the flag and break the loop
                        recent_dir_found=1
                        break
                    fi
                done

                # If no recent directories are found, rename the "laarchive" directory
                if [ "$recent_dir_found" -eq 0 ]
                then
                    new_dir_name="Previous-logs-${current_date_time}"
                    echo "$(date +"%Y-%m-%d %H:%M:%S") - Creating new directory: $new_dir_name"

                    # Change permissions for /mnt/archive/ and /mnt/archive/laarchive/
                    sudo chmod -R 777 /mnt/archive/

                    # Rename the "laarchive" directory
                    mv /mnt/archive/laarchive /mnt/archive/${new_dir_name}

                    # Recreate /mnt/archive/laarchive
                    mkdir /mnt/archive/laarchive
                    echo "$(date +"%Y-%m-%d %H:%M:%S") - Recreated /mnt/archive/laarchive directory."

                    echo "$(date +"%Y-%m-%d %H:%M:%S") - Changing permissions for /mnt/archive/laarchive/"
                    sudo chmod 777 /mnt/archive/laarchive
                else
                    echo "$(date +"%Y-%m-%d %H:%M:%S") - Recent directory found within 2 hours. Skipping creation."
                fi
            else
                echo "$(date +"%Y-%m-%d %H:%M:%S") - Directory with the same name pattern already exists for today. Skipping creation."
	        sleep 3600
            fi
        else
	    hrs=$((time_difference / 3600))
	    waitfor=$((86300 - time_difference))  
            echo "$(date +"%Y-%m-%d %H:%M:%S") - /mnt/archive/laarchive was created $hrs hr ago. Skipping directory operations for $waitfor."
	    sleep 3600
        fi
    else
        echo "$(date +"%Y-%m-%d %H:%M:%S") - Creating /mnt/archive/ and /mnt/archive/laarchive/"
        mkdir -p /mnt/archive/laarchive
        echo "$(date +"%Y-%m-%d %H:%M:%S") - Changing permissions for /mnt/archive/ and /mnt/archive/laarchive/"
        sudo chmod -R 777 /mnt/archive/
    fi
done


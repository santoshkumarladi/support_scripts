#!/bin/bash
#cd bin and copy this file.
## Run this script ./Marktaskfailed.sh
for task in `ecli task.list status_list=kQueued limit=10000 | awk '/kVm/{ print $1 }'`
do
  echo "Task ID is: " $task
    if
      grep -q "No matching specs found."  <<< $(nuclei diag.get_specs task=$task 2>/dev/null) ; then
        echo "task does not have valid spec - failing task"
        yes|python ~/bin/ergon_update_task --task_uuid=$task --task_status=failed;
      else
        echo "valid spec - moving on"
    fi
done

echo "Script finished"

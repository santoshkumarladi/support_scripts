#
# Copyright (c) 2016 Nutanix Inc. All rights reserved.
#
# Author: nick.neely@nutanix.com
#

[[ $(uname) == CYGWIN* ]] && IS_WINDOWS=true || IS_WINDOWS=false

# Echo a command and then run it as a daemon.
#
# Running the process as a daemon prevents it from hanging this shell if
# it gets stuck and refuses to exit.
#
# Input:
#   1: The path of the file to which all output from the command should
#     be written.
#   @: The command to be run and its arguments.
echo_and_run_daemon() {
  log_file="$1"
  shift
  echo
  echo "Running '$*' &>>$log_file"
  nohup "$@" &>>"$log_file" &
}

get_unix_time() {
  date '+%s'
}

process_is_alive() {
  pid=$1
  kill -0 $pid &>/dev/null
}

# Run fio for a specified amount of time.
#
# This function manages fio's lifecycle, including restarting it and
# killing it as necessary to run for the specified amount of time.
#
# Input:
#   1: The total runtime.
#   2: The path of the file to which all fio output should be written.
#   @: Arguments to fio. These should not include the '--runtime' option
#     and argument, which will be provided by this function.
#   FIO_* environment variables: For special-case tuning and testing of
#     this function.
run_timed_fio() {
  FIO_MAX_RUNTIME=${FIO_MAX_RUNTIME:-$(( 3 * 60 * 60 ))}
  FIO_TIMEOUT_BUFFER=${FIO_TIMEOUT_BUFFER:-$(( 60 * 60 ))}
  FIO_POLL_INTERVAL=${FIO_POLL_INTERVAL:-5}
  FIO_PRINT_STATS=${FIO_PRINT_STATS:-1}
  FIO_STATS_INTERVAL=${FIO_STATS_INTERVAL:-$(( 10 * 60 ))}

  total_runtime=$1
  fio_log="$2"
  shift 2

  now=$(get_unix_time)
  end_time=$(( $now + $total_runtime ))
  stats_time=$now
  fio_pid=""
  status=1

  rm -f "$fio_log"

  echo "Running fio for a total of $total_runtime seconds..."
  while true; do
    now=$(get_unix_time)

    if (( $FIO_PRINT_STATS == 1 && $now >= $stats_time )); then
      if ! $IS_WINDOWS; then
        echo
        echo "========== $(date) =========="
        top -b -n 1 | head -10
        echo
        ps ax | grep fio
      fi
      stats_time=$(( $stats_time + $FIO_STATS_INTERVAL ))
    fi

    if [[ -z "$fio_pid" ]]; then
      if (( $now >= $end_time )); then
        status=0
        break
      fi
      fio_runtime=$(( $end_time - $now ))
      if (( $fio_runtime > $FIO_MAX_RUNTIME )); then
        fio_runtime=$FIO_MAX_RUNTIME
      fi
      # Provide the runtime first so it applies to all jobs.
      echo_and_run_daemon "$fio_log" \
        sudo /usr/bin/fio --runtime=$fio_runtime "$@"
      fio_pid=$!
      fio_end_time=$(( $now + $fio_runtime ))
    elif process_is_alive $fio_pid; then
      if (( $now > $fio_end_time + $FIO_TIMEOUT_BUFFER )); then
        echo
        echo "Killing fio because it ran too long"
        kill -9 $fio_pid
        status=9
        break
      else
        sleep $FIO_POLL_INTERVAL
      fi
    else
      wait $fio_pid
      fio_status=$?
      if (( $fio_status == 0 )); then
        # Reset the fio PID so a new instance will be created the next
        # time through the loop.
        fio_pid=""
      else
        echo
        echo "Finishing early because fio exited with error status $fio_status"
        status=$fio_status
        break
      fi
    fi
  done

  echo
  echo "========== All fio output =========="
  cat "$fio_log"

  return $status
}

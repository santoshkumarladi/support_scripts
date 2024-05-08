#! /bin/bash

waitT=$1

set -x
while [ 1 ]
do
  #echo "(ps -eao pid,etimes,command | awk -v w="$waitT" '/acli / {if ($2 > w) { print $0}}')"
  (ps -eao pid,etimes,command | awk -v w="$waitT" '/cli / {if ($2 > w) { print $0}}')
  kill $(ps -eao pid,etimes,command | awk -v w="$waitT" '/cli / {if ($2 > w) { print $1}}')
sleep $waitT
done

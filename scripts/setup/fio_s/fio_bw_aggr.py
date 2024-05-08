#!/usr/bin/env python
#
# Copyright (c) 2013 Nutanix Inc. All rights reserved.
#
# Author: rohit@nutanix.com
#

import glob
import re
import sys

from fio_latency_aggr import aggr_latency

def main():
  if len(sys.argv) < 3:
    sys.exit(1)

  num_nodes = int(sys.argv[1])
  display_latency = len(sys.argv) > 3 and int(sys.argv[3]) != 0

  sum = 0
  lat_min_sum = 0
  lat_max_sum = 0
  lat_median_sum = 0

  # The result files have the same prefix followed by the IP address of the
  # host.
  files = glob.glob("%s*.out" % sys.argv[2])
  assert len(files) == num_nodes, "Found %d files instead of %d" % (
    len(files), num_nodes)

  for ff in sorted(files):
    fp = open(ff, "r")
    output = fp.readlines()
    fp.close()
    p = re.compile(r'.*io=.*, bw=(\d+)(\.\d+)?(M|K)B/s, iops=.*')
    for line in output:
      m = p.match(line)
      if m is not None:
        if m.group(3) == "M":
          sum = sum + 1024 * int(m.group(1))
        else:
          sum = sum + int(m.group(1))
        # Continue processing more lines as this might be a mixed W/L test, in
        # which case the read and write results are printed separately.

    if display_latency:
      latency = aggr_latency(output)
      if not latency or len(latency) != 3:
        sys.exit(1)

      lat_min_sum += latency[0]
      lat_max_sum += latency[1]
      lat_median_sum += latency[2]

  result = "%d MBps" % (sum/1024)

  if display_latency:
    result = "%s , latency(msec): min=%d, max=%d, median=%d" % (
      result, lat_min_sum / num_nodes, lat_max_sum / num_nodes,
      lat_median_sum / num_nodes)

  print result

if __name__ == "__main__":
  main()

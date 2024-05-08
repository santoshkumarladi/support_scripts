#!/usr/bin/env python
#
# Copyright (c) 2013 Nutanix Inc. All rights reserved.
#
# Author: binny@nutanix.com
#

import glob
import os
import re
import sys

def main():
  if len(sys.argv) < 3:
    sys.exit(1)

  num_nodes = int(sys.argv[1])
  results_path_prefix = sys.argv[2]

  test_name = os.path.basename(results_path_prefix).rstrip("_")
  sum_iops = 0
  sum_throughput = 0
  sum_iotime = 0 # Product of latency and IOPS.
  throughput_re = re.compile(r'.*io=.*, bw=(\d+)(\.\d+)?[K ]B/s, iops=(\d+).*')
  latency_re = re.compile(
    r'\s+lat \((\w+)\): min=\s*([\d.]+)\s*, max=\s*([\d.]+)\s*, '
    r'avg=\s*([\d.]+)\s*,')

  # The result files have the same prefix with IP address of the host in the end.
  files = glob.glob("%s*.out" % results_path_prefix)
  assert len(files) == num_nodes, "Found %d files instead of %d" % (
    len(files), num_nodes)

  print # Empty line for formatting.

  for ff in sorted(files):
    fp = open(ff, "r")
    output = fp.readlines()
    fp.close()
    throughput, iops, latency, lat_str = None, None, None, None
    ip = ff.rsplit("_", 1)[1]

    for line in output:
      m = throughput_re.match(line)
      if m is not None:
        throughput = float(m.group(1))
        iops = float(m.group(3))
        sum_throughput = sum_throughput + throughput
        sum_iops = sum_iops + iops

      m = latency_re.match(line)
      if m is not None:
        latency = float(m.group(4))
        lat_str = \
          "{avg:.1f} {units} (min:{min} {units}, max:{max} {units})".format(
            avg=latency, min=m.group(2), max=m.group(3), units=m.group(1))
        # Convert latency to msec.
        if m.group(1) == "usec":
          latency = latency / 1000
        if m.group(1) == "sec":
          latency = latency * 1000
        sum_iotime = sum_iotime + (latency * iops)

      if lat_str is not None:
        print "%s: Throughput: %.1f MBps, IOPS: %s, Latency: %s" % (
          ip, throughput/1024, iops, lat_str)
        # Continue processing more lines as this might be a mixed W/L test, in
        # which case the read and write results are printed separately.
        lat_str = None

  print "%s Total: %.1f MBps, %s IOPS, %.1f msec" % (
    test_name, sum_throughput/1024, sum_iops, sum_iotime/sum_iops)

if __name__ == "__main__":
  main()

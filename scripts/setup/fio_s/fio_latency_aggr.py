#!/usr/bin/env python
#
# Copyright (c) 2013 Nutanix Inc. All rights reserved.
#
# Author: tabrez@nutanix.com
#
# This should be the first line. It sets up the python environment
import diagnostics_env

import re

from util.base import log

def aggr_latency(fio_test_output):
  """
  Returns a tuple containing (min, max, median) latency extracted from the
  output of the fio test specified in fio_test_output. Returns None on error.
  """

  lat_min = 0
  lat_max = 0
  lat_median = 0

  pct_time_scale_msecs = None

  lat_minmax_re = re.compile(r'^lat \(([mu])sec\): min=(\d+), max=(\d+)')
  lat_median_re = re.compile(r'.*50.00th=\[(.*)\], .*')
  lat_percentile_unit_re = re.compile(r'^clat percentiles \(([um])sec\)')

  for line in fio_test_output:
    line = line.strip()

    # Determine unit in which the percentile latency is reported (usec/msec).
    m = lat_percentile_unit_re.match(line)
    log.DEBUG("matched {0}".format(line))
    if m is not None:
      if m.group(1) == "u":
        pct_time_scale_msecs = 1000
      else:
        assert m.group(1) == "m"
        pct_time_scale_msecs = 1

    # Look for min/max latency report.
    m = lat_minmax_re.match(line)
    if m is not None:
      time_scale_msecs = 1
      if m.group(1) == "u":
        time_scale_msecs = 1000

      lat_min = (int(m.group(2)) / time_scale_msecs)
      lat_max = (int(m.group(3)) / time_scale_msecs)

    # Look for 50th percentile latency report to determine median.
    m = lat_median_re.match(line)
    if m is not None:
      # We should have seen the line with the unit for the percentile value by
      # now.
      if not pct_time_scale_msecs:
        return None
      lat_median = (int(m.group(1)) / pct_time_scale_msecs)

  return (lat_min, lat_max, lat_median)

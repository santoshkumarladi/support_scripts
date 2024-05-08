import logging
import contextlib
import os
import re
import datetime
import time
import random
import sys, subprocess

log = logging.getLogger(__name__)



class FVTWorkload(object):
   '''
   Base class for all FVT related workloads
   '''
   # pylint: disable=R0913
   FIO_CMD = ["/usr/bin/fio"]
   FIO_LOAD_OUTPUT = "/root/fio-workload"
   FIO_LOAD_LOG = '/tmp/fio-workload.log'

   #FIO_ARGS = ["--ioengine=libaio",
   FIO_ARGS = ["--ioengine=libaio",
               "--name=job1",
               "--direct=1",
	       "--overwrite=1",
	       "--do_verify=1",
	       "--rwmixwrite=100",
	       #"--rwmixwrite=30",
	       "--iodepth_batch=2",
	       "--iodepth_batch_complete=2",
	       "--verify_fatal=1",
	       "--verify_dump=1",
	       "--time_based",
	       #"--rate=80K,80K",
	       "--rate=300m,1000K",
	       #"--rate_iops=3",
	       "--buffer_compress_percentage=50",
	       "--refill_buffers",
	       #"--buffer_pattern=shivayogidavanageri",
	       #"--rate=50m,256k",
               #"--verify=sha1"
               "--verify=md5"
              ]


def FIO_Cmd(**kwargs):
      cmd = []
      bsrange = kwargs.pop('bsrange', None)
      if bsrange:
         cmd.extend(["--bsrange=%s" % bsrange])
      bssplit = kwargs.pop('bssplit', None)
      if bssplit:
         cmd.extend(["--bssplit=%s" % bssplit])
      bs = kwargs.pop('bssplit', None)
      if bs:
         # default is 4k(read and write)
         # or 4k,8k,4k (read, write, trim)
         cmd.extend(["--bs=%s" % bs])
      filename = kwargs.pop('filename', None)
      if not filename:
         filename = FVTWorkload.FIO_LOAD_OUTPUT

      if kwargs.pop('run_verify', None):
         cmd.extend(["--do_verify=%s" % kwargs.pop('do_verify', 1)])
         cmd.extend(["--verify=md5"])

      compchunk = kwargs.pop('compchunk', None)
      if compchunk:
         # defaults to blocksize
         cmd.extend(["--buffer_compress_chunk=%s" % compchunk])

      compratio = kwargs.pop('compratio', None)
      if compratio:
         cmd.extend(
            ["--buffer_compress_percentage=%d" % compratio])
         cmd.extend(["--refill_buffers=1"])  

      loops = kwargs.pop('loops', None)
      if loops:
         cmd.extend(["--loops=%d" % loops])

      overwrite = kwargs.pop('overwrite', None)
      if overwrite:
         cmd.extend(["--overwrite=1"])

      # generate sequential/random read/writes
      cmd.extend(["--rw=%s" % kwargs.pop('rw'),
              "--size=%s" % kwargs.pop('size'),
              "--iodepth=%d" % kwargs.pop('iodepth'),
              "--numjobs=%d" % kwargs.pop('numjobs'),
              "--filename=%s" % filename
             ])

      for k, v in kwargs.items():
         cmd.extend(["--%s=%s" % (k, str(v))])

      wlcmd = FVTWorkload.FIO_CMD + cmd + FVTWorkload.FIO_ARGS
      return wlcmd


def runFIO(cmd):
	FIOfinalcmd = cmd
	#subprocess.call(FIOfinalcmd, shell=True)
	os.system(FIOfinalcmd + "&")
	return 
	


if __name__ == "__main__":
	while True:
		#bslist1 = [ '4K', '6K', '8K' ]
		#bslist1 = [ '8K', '16K' ]
		#bslist1 = [ '4K', '5K', '6K', '7K', '8K', '16K' ]
		#bslist1 = [ '4K', '5K', '6K', '7K', '8K', '16K', '32K', '64K' ]
		#bslist1 = [ '4K', '8K' , '16K', '32K', '64K', '128K', '256K' , '512K' , '1M' ]
		bslist1 = [ '4K', '8K' , '16K', '32K', '64K', '128K', '256K' , '512K' , '1M' , '2M' , '4M' ]
		startoffset = 0
		iodep = 4 
		#x = str(random.randint(1,1024)) + "K"
		#bslist1 = str(random.randint(1,1024)) + "K"
		for x in bslist1:	
			#runcmd=FIO_Cmd(bs = x, rw = 'readwrite', runtime = '1800', offset = '0', size = '9G', numjobs = 1 , iodepth = iodep, filename = '/dev/sdb' )
			#runcmd=FIO_Cmd(bs = x, bssplit = '4K/40:8K/50:16K/10', rw = 'read', runtime = '7200', offset = '0', size = '8G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			runcmd=FIO_Cmd(bs = x, bssplit = '8K/50:16K/50', rw = 'readwrite', runtime = '7200', offset = '0', size = '800G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			#runcmd=FIO_Cmd(bs = x, bssplit = '4K/40:8K/50:16K/10', rw = 'readwrite', runtime = '7200', offset = '0', size = '8G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			##runcmd=FIO_Cmd(bs = x, rw = 'readwrite', runtime = '1800', offset = '0', size = '8G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			finalCmd = " ".join(runcmd)
		        outputfile = runFIO(finalCmd)

			runcmd1=FIO_Cmd(bs = x, bssplit = '4K/40:8K/50:32K/10', rw = 'read', runtime = '7200', offset = '8G', size = '200G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			#runcmd1=FIO_Cmd(bs = x, bssplit = '8K/50:32K/50', rw = 'readwrite', runtime = '7200', offset = '8G', size = '2G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			#runcmd1=FIO_Cmd(bs = x, bssplit = '4K/40:8K/50:32K/10', rw = 'readwrite', runtime = '7200', offset = '8G', size = '2G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			##runcmd1=FIO_Cmd(bs = x, rw = 'randrw', runtime = '1800', offset = '8G', size = '2G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
               		finalCmd1 = " ".join(runcmd1)
		        outputfile1 = runFIO(finalCmd1)

			time.sleep(9000)	

			#runcmd2=FIO_Cmd(bs = x, bssplit = '4K/40:8K/50:16K/10', rw = 'randread', runtime = '7200' , offset = '0', size = '8G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			runcmd2=FIO_Cmd(bs = x, bssplit = '8K/50:16K/50', rw = 'randrw', runtime = '7200' , offset = '0', size = '800G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			#runcmd2=FIO_Cmd(bs = x, bssplit = '4K/40:8K/50:16K/10', rw = 'randrw', runtime = '7200' , offset = '0', size = '8G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
		##	runcmd2=FIO_Cmd(bs = x,  rw = 'randrw', runtime = '600' , offset = '0', size = '8G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			finalCmd2 = " ".join(runcmd2)
		        outputfile2 = runFIO(finalCmd2)
		#	time.sleep(900)	
			#runcmd1=FIO_Cmd(bs = x, rw = 'randrw', runtime = '1800', offset = '0', size = '9G', numjobs = 1 , iodepth = iodep, filename = '/dev/sdb' )
			##runcmd1=FIO_Cmd(bs = x, bssplit = '8K/90:32K/10', rw = 'randrw', runtime = '7200', offset = '8G', size = '10G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			##runcmd1=FIO_Cmd(bs = x, rw = 'randrw', runtime = '1800', offset = '8G', size = '2G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
               		##finalCmd1 = " ".join(runcmd1)
		        ##outputfile1 = runFIO(finalCmd1)

			#runcmd3=FIO_Cmd(bs = x, bssplit = '4K/40:8K/50:32K/10', rw = 'randread', runtime = '7200', offset = '8G', size = '2G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			#runcmd3=FIO_Cmd(bs = x, bssplit = '8K/50:32K/50', rw = 'randrw', runtime = '7200', offset = '8G', size = '2G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			#runcmd3=FIO_Cmd(bs = x, bssplit = '4K/40:8K/50:32K/10', rw = 'randrw', runtime = '7200', offset = '8G', size = '2G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
			runcmd1=FIO_Cmd(bs = x, rw = 'randrw', runtime = '1800', offset = '8G', size = '200G', numjobs = 8 , iodepth = iodep, filename = '/dev/sdb' )
               		finalCmd3 = " ".join(runcmd3)
		        outputfile3 = runFIO(finalCmd3)

			time.sleep(9000)	

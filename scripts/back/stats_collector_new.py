#!/usr/bin/python
#
# Copyright (c) 2018 Nutanix Inc. All rights reserved.
#
# Author: kranti.yadhati@nutanix.com
#
# Grab Curator, cassandra and stargate stats
# USAGE:
# python stats_collector.py

import os
import re
import requests
import sys
import time
import paramiko
#import pxssh
from pexpect import pxssh
import socket
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError

class stats_collector(object):

  curator_master_pages = {"scan_times" : "2010", "tier_usage" : "2010/master/tierusage", \
  "rebuild_info" : "2010/master/rebuildinfo", "map_reduce_tasks" : "2010/master/mapreduce/tasks", \
  "background_tasks" : "2010/master/backgroundtasks"}
  curator_job_tasks = {"curator_job_tasks" : "2010/master/jobexecution?execution_id="}
  curator_slave_pages = {"map_reduce_tasks" : "2010"}
  chronos_pages = {"chronos" : "2011"}
  stargate_pages = {"stargate" : "2009", "h_vars_medusa" : "2009/h/vars?regex=medusa", \
  "admctl_stats" : "2009/admctl_queue_stats", "estore_disk_stats" : "2009/estore_disk_stats", \
  "disk_queue_stats" : "2009/disk_queue_stats"}
  cassandra_pages = {"cassandra_2040" : "2040"}
  ssh_commands = {"garbage_printer" : "curator_cli display_garbage_report include_tier_info=true", \
  "snapshot_tree" : "snapshot_tree_printer", "egroup_access_info" : "curator_cli get_disk_egroup_access_info", "curator_counters" : "curator_cli get_counter_info counter_names=all"}

  def __init__(self, **kwargs):
    self.file_path = kwargs.get("file_path", '/tmp')
    self.virtual_ip = kwargs.get("virtual_ip", '0.0.0.0')
    self.timestr = time.strftime("%Y%m%d-%H%M%S")
    self.ssh_client = paramiko.SSHClient()
    #self.ssh_client.set_missing_host_key_policy(client.AutoAddPolicy())
    self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.run_ssh_cmd('uptime')
    self.master_ip = self.get_master()
    self.all_nodes = self.get_all_nodes()
  
  def run_ssh_cmd(self, cmd):
    try:
      #self.ssh_client.connect(self.virtual_ip, 22, "nutanix", "nutanix/4u")
      s = pxssh.pxssh()
      if not s.login (self.virtual_ip, "nutanix", "nutanix/4u"):
        print "No SSH connection"
        print str(s)
        return
      else:
        print "SSH login sucessful"
        stdin, stdout, stderr = s.sendline (cmd)
        output = stdout.read()
        s.prompt
        print s.before()
        s.logout()
        return output

 
#  def run_ssh_cmd(self, cmd):
#    try:
#      #self.ssh_client.connect(self.virtual_ip, 22, "nutanix", "nutanix/4u")
#      self.ssh_client.connect(self.virtual_ip, port=22, username="nutanix", password="nutanix/4u", look_for_keys=False, pkey=None)
#      stdin, stdout, stderr = self.ssh_client.exec_command(cmd, bufsize=-1, timeout=60)
#      output = stdout.read()
#      self.ssh_client.close()
#      return output 
#    except socket.error as e:
#      print "No SSH connection"
#      return

  def get_all_nodes(self):
    cmd = 'source /etc/profile;' + 'svmips'
    output = self.run_ssh_cmd(cmd)
    all_nodes = output.split()
    return all_nodes
  
  def check_and_create_dir(self,directory):
    if not os.path.exists(directory):
      print "Creating directory %s" %directory
      os.makedirs(directory)

  def get_response(self,ip,url):
    try:
      response = requests.get("http://%s:%s" %(ip,url))
      return response
    except ConnectionError:
      return

  def get_master(self):
    cmd = "source /etc/profile;" + "zkcat /appliance/logical/leaders/curator/$"\
          + "(zkls /appliance/logical/leaders/curator | sort | head -1) | cut -d':' -f2 | awk {'print $1'}"
    output = self.run_ssh_cmd(cmd)
    if output.strip():
      master_ip = output.strip().split()[0]
      return master_ip
    else:
      print "Could not find Curator master"
      return

  def get_stats_from_ssh(self): 
    for stat,cmd in stats_collector.ssh_commands.items():
      self.check_and_create_dir('%s/%s' %(self.file_path,stat))
      cmd = 'source /etc/profile;' + cmd
      output = self.run_ssh_cmd(cmd)
      with open('%s/%s/%s' %(self.file_path,stat,self.timestr) , 'w') as file:
        file.write(output)

  def get_curator_master_pages(self):
  # Collect curator master page stats
    for stat,url in stats_collector.curator_master_pages.items():
      if stat is 'map_reduce_tasks': 
        self.check_and_create_dir('%s/%s/%s' %(self.file_path,stat,self.master_ip))
        response = self.get_response(self.master_ip,url)
        if response:
          with open('%s/%s/%s/%s' %(self.file_path,stat,self.master_ip,self.timestr) , 'w') as file:
            file.write(response.text)
      else:
        self.check_and_create_dir('%s/%s' %(self.file_path,stat))
        response = self.get_response(self.master_ip,url)
        if response:
          with open('%s/%s/%s' %(self.file_path,stat,self.timestr) , 'w') as file:
            file.write(response.text)

  def get_curator_job_task_stats(self):
  # Collect curator job task stats
    cmd = 'source /etc/profile;' + 'curator_cli get_last_successful_scans | grep -A2 Full | tail -n1 | awk {\'print $5\'}'
    output = self.run_ssh_cmd(cmd)
    output = output.strip()
    for stat,url in stats_collector.curator_job_tasks.items():
      self.check_and_create_dir('%s/%s' %(self.file_path,stat))
      url = url + output
      response = self.get_response(self.master_ip,url)
      if response:
        with open('%s/%s/%s' %(self.file_path,stat,self.timestr) , 'w') as file:
          file.write(response.text)

  def get_chronos_page(self):
  # Collect chronos stats
    for stat,url in stats_collector.chronos_pages.items():
      self.check_and_create_dir('%s/%s' %(self.file_path,stat))
      response = self.get_response(self.master_ip,url)
      if response:
        with open('%s/%s/%s' %(self.file_path,stat,self.timestr) , 'w') as file:
          file.write(response.text)

  def get_curator_slave_pages(self):
  # Collect curator slave stats
    for stat,url in stats_collector.curator_slave_pages.items():
      for node in self.all_nodes:
        self.check_and_create_dir('%s/%s/%s' %(self.file_path,stat,node))
        if node == self.master_ip:
          continue
        response = self.get_response(node,url)
        if response:
          with open('%s/%s/%s/%s' %(self.file_path,stat,node,self.timestr) , 'w') as file:
            file.write(response.text)

  def get_cassandra_pages(self):
  # Collect cassandra stats
    for stat,url in stats_collector.cassandra_pages.items():
      for node in self.all_nodes:
        self.check_and_create_dir('%s/%s/%s' %(self.file_path,stat,node))
        response = self.get_response(node,url)
        if response:
          with open('%s/%s/%s/%s' %(self.file_path,stat,node,self.timestr) , 'w') as file:
            file.write(response.text)

  def get_stargate_pages(self):
  # Collect stargate stats
    for stat,url in stats_collector.stargate_pages.items():
      for node in self.all_nodes:
        self.check_and_create_dir('%s/%s/%s' %(self.file_path,stat,node))
        response = self.get_response(node,url)
        if response:
          with open('%s/%s/%s/%s' %(self.file_path,stat,node,self.timestr) , 'w') as file:
            file.write(response.text)

if len (sys.argv) < 3:
  print("Syntax: script-name.exp <vitual-ip> <path>")
  sys.exit(1)
else:
  cluster = stats_collector(file_path=sys.argv[2], virtual_ip=sys.argv[1])
  cluster.get_stats_from_ssh()
  cluster.get_curator_master_pages()
  cluster.get_curator_job_task_stats()
  cluster.get_chronos_page()
  cluster.get_curator_slave_pages()
  cluster.get_cassandra_pages()
  cluster.get_stargate_pages()

# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=unused-variable
# pylint: disable=no-self-use
# pylint: disable=ungrouped-imports

"""
Copyright (c) 2018 Nutanix Inc. All rights reserved.
Author: kranti.yadhati@nutanix.com
Grab Curator, cassandra and stargate stats
USAGE: python stats_collector.py
"""

import os
import sys
import time
from socket import error as SocketError
from paramiko import client
from requests import get
from requests.exceptions import ConnectionError

class stats_collector(object):
  """
    Base class to collect all stats for various CDP processes
  """

  curator_master_pages = {"scan_times" : "2010", "tier_usage" : "2010/master/tierusage", \
  "rebuild_info" : "2010/master/rebuildinfo", "map_reduce_tasks" : "2010/master/mapreduce/tasks", \
  "background_tasks" : "2010/master/backgroundtasks"}
  curator_job_tasks = {"curator_job_tasks" : "2010/master/jobexecution?execution_id="}
  curator_slave_pages = {"map_reduce_tasks" : "2010"}
  chronos_pages = {"chronos" : "2011"}
  stargate_pages = {"stargate" : "2009", "h_vars_medusa" : "2009/h/vars?regex=medusa", \
  "admctl_stats" : "2009/admctl_queue_stats", "estore_disk_stats" : "2009/estore_disk_stats", \
  "disk_queue_stats" : "2009/disk_queue_stats", "cache_stats" : "2009/cache_stats", \
  "corrupt_egroups" : "2009/corrupt_egroups"}
  cassandra_pages = {"cassandra_2040" : "2040", "cassandra_admctl" : "2040/AllAdmctlStats", "cassandra_leader_only" : "2040/h/leader_only_scan_stats"}
  ssh_commands = {"garbage_printer" : "curator_cli display_garbage_report include_tier_info=true", \
  "snapshot_tree" : "snapshot_tree_printer", "egroup_access_info" : "curator_cli get_disk_egroup_access_info", \
  "curator_counters" : "curator_cli get_counter_info counter_names=all"}

  def __init__(self, **kwargs):
    """
    Collect stargate stats
    Args:
    Returns:
    """
    self.file_path = kwargs.get("file_path", '/tmp')
    self.virtual_ip = kwargs.get("virtual_ip", '0.0.0.0')
    self.timestr = time.strftime("%Y%m%d-%H%M%S")
    self.ssh_client = client.SSHClient()
    self.ssh_client.set_missing_host_key_policy(client.AutoAddPolicy())
    self.run_ssh_cmd('uptime')
    self.master_ip = self.get_master()
    self.all_nodes = self.get_all_nodes()

  def run_ssh_cmd(self, cmd):
    """
    Run ssh command on CVM
    Args:
      cmd(str): Command to be run
    Returns:
    """
    try:
      self.ssh_client.connect(self.virtual_ip, 22, "nutanix", "nutanix/4u")
      stdin, stdout, stderr = self.ssh_client.exec_command(cmd, bufsize=-1, timeout=60)
      output = stdout.read()
      self.ssh_client.close()
      return output
    except SocketError:
      print "SSH connection failure with socket error"
      return

  def get_all_nodes(self):
    """
    Collect stargate stats
    Args:
    Returns:
    """
    cmd = 'source /etc/profile;' + 'svmips'
    output = self.run_ssh_cmd(cmd)
    all_nodes = output.split()
    return all_nodes

  def check_and_create_dir(self, directory):
    """
    Check if dir exists and create if no
    Args:
      directory(str): Directory to be created
    Returns:
    """
    if not os.path.exists(directory):
      print "Creating directory %s" %directory
      os.makedirs(directory)

  def get_response(self, ip, url):
    """
    Get webpage
    Args:
      ip(str): IP of the node
      url(str): Weboage URL
    Returns:
    """
    try:
      response = get("http://%s:%s" %(ip, url))
      return response
    except ConnectionError:
      return

  def get_master(self):
    """
    Collect stargate stats
    Args:
    Returns:
    """
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
    """
    Collect stargate stats
    Args:
    Returns:
    """
    for stat, cmd in stats_collector.ssh_commands.items():
      self.check_and_create_dir('%s/%s' %(self.file_path, stat))
      cmd = 'source /etc/profile;' + cmd
      output = self.run_ssh_cmd(cmd)
      with open('%s/%s/%s' %(self.file_path, stat, self.timestr), 'w') as output_file:
        output_file.write(output)

  def get_curator_master_pages(self):
    """
    Collect stargate stats
    Args:
    Returns:
    """
  # Collect curator master page stats
    for stat, url in stats_collector.curator_master_pages.items():
      if stat is 'map_reduce_tasks':
        self.check_and_create_dir('%s/%s/%s' %(self.file_path, stat, self.master_ip))
        response = self.get_response(self.master_ip, url)
        if response:
          with open('%s/%s/%s/%s' %(self.file_path, stat, self.master_ip, self.timestr), 'w') as output_file:
            output_file.write(response.text)
      else:
        self.check_and_create_dir('%s/%s' %(self.file_path, stat))
        response = self.get_response(self.master_ip, url)
        if response:
          with open('%s/%s/%s' %(self.file_path, stat, self.timestr), 'w') as output_file:
            output_file.write(response.text)

  def get_curator_job_task_stats(self):
    """
    Collect stargate stats
    Args:
    Returns:
    """
  # Collect curator job task stats
    cmd = 'source /etc/profile;' + 'curator_cli get_last_successful_scans | grep -A2 Full | tail -n1 | awk {\'print $5\'}'
    output = self.run_ssh_cmd(cmd)
    output = output.strip()
    for stat, url in stats_collector.curator_job_tasks.items():
      self.check_and_create_dir('%s/%s' %(self.file_path, stat))
      url = url + output
      response = self.get_response(self.master_ip, url)
      if response:
        with open('%s/%s/%s' %(self.file_path, stat, self.timestr), 'w') as output_file:
          output_file.write(response.text)

  def get_chronos_page(self):
    """
    Collect stargate stats
    Args:
    Returns:
    """
  # Collect chronos stats
    for stat, url in stats_collector.chronos_pages.items():
      self.check_and_create_dir('%s/%s' %(self.file_path, stat))
      response = self.get_response(self.master_ip, url)
      if response:
        with open('%s/%s/%s' %(self.file_path, stat, self.timestr), 'w') as output_file:
          output_file.write(response.text)

  def get_curator_slave_pages(self):
    """
    Collect stargate stats
    Args:
    Returns:
    """
  # Collect curator slave stats
    for stat, url in stats_collector.curator_slave_pages.items():
      for node in self.all_nodes:
        self.check_and_create_dir('%s/%s/%s' %(self.file_path, stat, node))
        if node == self.master_ip:
          continue
        response = self.get_response(node, url)
        if response:
          with open('%s/%s/%s/%s' %(self.file_path, stat, node, self.timestr), 'w') as output_file:
            output_file.write(response.text)

  def get_cassandra_pages(self):
    """
    Collect stargate stats
    Args:
    Returns:
    """
    for stat, url in stats_collector.cassandra_pages.items():
      for node in self.all_nodes:
        self.check_and_create_dir('%s/%s/%s' %(self.file_path, stat, node))
        response = self.get_response(node, url)
        if response:
          with open('%s/%s/%s/%s' %(self.file_path, stat, node, self.timestr), 'w') as output_file:
            output_file.write(response.text)

  def get_stargate_pages(self):
    """
    Collect stargate stats
    Args:
    Returns:
    """
    for stat, url in stats_collector.stargate_pages.items():
      for node in self.all_nodes:
        self.check_and_create_dir('%s/%s/%s' %(self.file_path, stat, node))
        response = self.get_response(node, url)
        if response:
          with open('%s/%s/%s/%s' %(self.file_path, stat, node, self.timestr), 'w') as output_file:
            output_file.write(response.text)

if len(sys.argv) < 3:
  print "Syntax: script-name.exp <vitual-ip> <path>"
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

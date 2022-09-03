#!/bin/python3.6
import subprocess, sys
from socket import gethostname as hostname
from ioperf import ioperf
from logqueue import queuethis
from etcdput import etcdput as put
from etcdgetpy import etcdget as get 
from etcddel import etcddel as dels
from poolstoimport import getpoolstoimport
from time import time as stamp
from ast import literal_eval as mtuple


#leader=get('leader','--prefix')[0][0].split('/')[1]
leader=''
stamp = str(stamp())


def selecthost(minhost,hostname,hostpools):
 if len(hostpools) < minhost[1]:
  minhost = (hostname, len(hostpools))
 return minhost


def dosync(*args):
  global leader
  put(*args)
  put(args[0]+'/'+leader,args[1])
  return 

def zpooltoimport(leader, myhost):
 needtoimport=get('needtoimport', myhost) 
 if myhost not in str(needtoimport):
  print('no need to import a pool here')
 else:
  for poolline in needtoimport:
   pool = poolline[0].replace('needtoimport/','')
   ioperf()
   print('pool', pool)
   cmdline= '/usr/sbin/zpool import  '+pool
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   cmdline= '/usr/sbin/zpool status  '
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   if pool in result:
    put('pools/'+pool,myhost)
    dosync('sync/pools/Add_'+pool+'_'+myhost+'/request','pools_'+stamp)
    cmdline= 'systemctl restart zfs-zed  '
    result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   dels('needtoimport',pool)
    
 if myhost != leader:
  return

 knowns=get('ready','--prefix')
 hosts=get('hosts','/current')
 pools = getpoolstoimport()
 needtoimport=get('needtoimport', '--prefix') 
 for pool in pools:
  if pool not in str(needtoimport):
   minhost=(myhost,float('inf'))
   for host in hosts: 
    hostname = host[0].split('/')[1]
    hostpools=mtuple(host[1])
    minhost = selecthost(minhost,hostname,hostpools)
   put('needtoimport/'+pool,minhost[0])
 return
     
       
if __name__=='__main__':
 if len(sys.argv) > 1:
  leader = sys.argv[1]
  myhost = sys.argv[2]
 else:
  leader=get('leader','--prefix')[0][0].split('/')[1]
  myhost = hostname()

 #cmdline='cat /pacedata/perfmon'
 #perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)
 #if '1' in perfmon:
 # queuethis('zpooltoimport.py','start','system')
 zpooltoimport(leader, myhost)
 #if '1' in perfmon:
 # queuethis('zpooltoimport.py','stop','system')

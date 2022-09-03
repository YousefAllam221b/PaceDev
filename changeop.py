#!/bin/python3.6
import subprocess,sys
import json
from logqueue import queuethis
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from etcdput import etcdput as put
from poolall import getall as getall
from poolall import putall as putall
from poolall import delall as delall
import logmsg
def forceoffline(*args):
 with open('/root/changeop','w') as f:
  f.write(str(args))
 alls=getall(args[0])
 mypools=[x for x in alls['pools'] if 'pree' not in x['name'] ]  
 for mypool in mypools:
  if args[1] in str(mypool):
   cmdline='/sbin/zpool offline '+mypool['name']+' '+args[1]
   subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
 return
def changeop(*args):
 alls=getall(args[0])
 if type(alls) != dict :
  return -1
 if len(args) > 1:
  if args[1] == 'old':
   putall(args[0],'old')
   return 1
 oldlls=getall(args[0],'old')
 if type(oldlls) != dict :
  for disk in alls['defdisks']:
   logmsg.sendlog('Diwa1','warning','system', disk['pool'])
   cmdline='/sbin/zpool offline '+disk['pool']+' '+disk['name']
   subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  putall(args[0],'old')
  return
 changeddisks={k:alls[k] for k in alls if alls[k] != oldlls[k] and 'disk' in k} 
 print('changed',len(changeddisks))
 if len(changeddisks) > 0:
  delall(args[0],'old')
 


if __name__=='__main__':
 with open('/pacedata/perfmon','r') as f:
  perfmon = f.readline() 
 if '1' in perfmon:
  queuethis('changeop.py','start','system')
 if len(sys.argv) > 2 and 'scsi' in sys.argv[2]:
   forceoffline(*sys.argv[1:])
 else: 
   changeop(*sys.argv[1:])
 if '1' in perfmon:
  queuethis('changeop.py','stop','system')

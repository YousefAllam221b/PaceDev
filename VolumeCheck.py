#!/bin/python3.6
import subprocess,sys, os
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from broadcasttolocal import broadcasttolocal 
from time import time as stamp

from socket import gethostname as hostname

#leader=get('leader','--prefix')[0][0].split('/')[1]

def dosync(leader, *args):
  put(*args)
  put(args[0]+'/'+leader,args[1])
  return 

def cifs(leader, myhost, etcds, replis, pcss):
 cmdline = 'docker ps'
 dockers = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8') 
 cmdline = '/TopStor/getvols.sh cifs'
 result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
 result = [x for x in result if 'pdhc' in x]
 print('###############3')
 print('cifs result', result)
 for res in result:
  reslist=res.split('/')
  if reslist[1] not in str(etcds):
   print('update',reslist[1], str(etcds))
   left='volumes/CIFS/'+myhost+'/'+'/'.join(reslist[0:2])
   put(left,res)
   dosync(leader, 'sync/volumes/'+myhost+'/request','volumes_'+str(stamp()))
   #broadcasttolocal(left,res)
  if 'active' in res:
   if (('cifs-'+reslist[7]) not in dockers) or (('cifs-'+reslist[7]) not in pcss):
    if 'DOMAIN' in res:
     cmdline='/TopStor/cifsmember.sh '+reslist[0]+' '+reslist[1]+' '+reslist[7]+' '+reslist[8]+' cifs '+' '.join(reslist[9:])
    else:
     cmdline='/TopStor/cifs.sh '+reslist[0]+' '+reslist[1]+' '+reslist[7]+' '+reslist[8]+' cifs'
    result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

def homes(leader, myhost, etcds, replis, pcss):
  cmdline = 'docker ps'
  dockers = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8') 
  cmdline = '/TopStor/getvols.sh home'
  result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
  result = [x for x in result if 'pdhc' in x]
  print('###############3')
  for res in result:
   reslist=res.split('/')
   if reslist[1] not in str(etcds):
    left='volumes/HOME/'+myhost+'/'+'/'.join(reslist[0:2])
    put(left,res)
    dosync(leader, 'sync/volumes/'+myhost+'/request','volumes_'+str(stamp()))
    #broadcasttolocal(left,res)
   if reslist[7] not in dockers or reslist[7] not in pcss:
    print(reslist)
    cmdline='/TopStor/cifs.sh '+reslist[0]+' '+reslist[1]+' '+reslist[7]+' '+reslist[8]+' cifs'
    result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)
    
   
def iscsi(leader, myhost, etcds, replis, pcss):
 cmdline = 'targetcli ls '
 targets = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8') 
 cmdline = '/TopStor/getvols.sh iscsi'
 result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
 result = [x for x in result if 'pdhc' in x]
 print('###############3')
 for res in result:
  reslist=res.split('/')
  if reslist[1] not in str(etcds):
   left='volumes/ISCSI/'+myhost+'/'+'/'.join(reslist[0:2])
   put(left,res)
   dosync(leader, 'sync/volumes/'+myhost+'/request','volumes_'+str(stamp()))
   #broadcasttolocal(left,res)
  if reslist[1] not in targets or reslist[2] not in pcss:
   print(reslist)
   cmdline='/TopStor/iscsi.sh '+reslist[0]+' '+reslist[1]+' '+reslist[2]+' '+reslist[3]+' '+ \
           reslist[4]+' '+reslist[5]+' '+reslist[6]+' '+reslist[7]
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   print(cmdline)
def volumecheck(leader, myhost, etcds, replis, pcss):
 cifs(leader,myhost, etcds, replis, pcss)
 homes(leader, myhost, etcds, replis, pcss)
 iscsi(leader, myhost, etcds, replis, pcss)
  
   
if __name__=='__main__':
 if len(sys.argv) > 1:
  leader = sys.argv[1]
  myhost = sys.argv[2]
 else:
  leader=get('leader','--prefix')[0][0].split('/')[1]
  myhost = hostname()
 
 etcds = get('volumes','--prefix')
 replis = get('replivol','--prefix')
 cmdline = 'pcs resource'
 pcss = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8') 
 volumecheck(leader, myhost, etcds, replis, pcss)

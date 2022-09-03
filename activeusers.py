#!/bin/python3.6
import sys
import subprocess
from etcddel import etcddel as etcddel
from etcdgetpy import etcdget as get 
from etcdput import etcdput as put 
from socket import gethostname as hostname


def activeusers(leader, myhost):
 cmdline = 'docker ps'
 result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
 result = [ x for x in result if 'cifs' in x ] 
 activeshares = [ (x.split()[0], x.split('cifs-')[1] ) for x in result ]
 conndict = {}
 for x in activeshares:
  cmdline = 'docker exec -t '+x[0]+' smbstatus -b '
  conndict[x[1]] = [] 
  result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
  conns = [ (y.split()[1],y.split()[3]) for y in result.split('\n') if 'SMB' in y ]
  connx1user = ''
  connx1dev = ''
  for conn in conns:
   conndict[x[1]].append({'user':conn[0], 'ip':conn[1]}) 
   connx1user = connx1user+conn[0]+'/'
   connx1dev = connx1dev+conn[1]+'/'
  if len(connx1user) > 0:
   connx1user = connx1user[:-1]
   connx1dev = connx1dev[:-1]
  if len(connx1user) > 0:
   put('connections/user/'+x[0]+'/'+x[1], connx1user)
   put('connections/dev/'+x[0]+'/'+x[1], connx1dev)
  else:
   etcddel('connections',x[0])

if __name__=='__main__':
 if len(sys.argv) > 1:
  leader = sys.argv[1]
  myhost = sys.argv[2]
 else:
  leader=get('leader','--prefix')[0][0].split('/')[1]
  myhost = hostname()
 activeusers(leader, myhost)

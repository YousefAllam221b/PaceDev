#!/bin/python3.6
import traceback, hashlib
import subprocess
from ast import literal_eval as mtuple
from etcddel import etcddel as dels
from etcdput import etcdput as put 
import socket
myhostorg=socket.gethostname()
cmdline = 'docker ps'
result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
activeshares = [ (x.split()[0],[z for z in x.split() if 'pdhcp' in z][0].split('-')[2]) for x in result.split('\n') if 'smb' in x] 
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
  dels('connections',x[0])


#!/bin/python3.6
import subprocess,socket
from ast import literal_eval as mtuple
import json
from time import sleep

myname=socket.gethostname()
myip=socket.gethostbyname(myname)
endpoints=''
cluster=''
data=json.load(open('/pacedata/runningetcdnodes.txt'))
for x in data['members']:
 endpoints+=str(x['clientURLs'])[2:][:-2]
 for y in x['peerURLs']:
  cluster+=str(x['name'])+'='+str(y)+','
 print(cluster) 
cmdline=['./etcdget.py','promote','--prefix']
promote=subprocess.run(cmdline,stdout=subprocess.PIPE)
if myname in str(promote.stdout): 
 cluster_state='existing'
 token='token-01'
 thisname=myname
 thisip=myip
 cluster+=thisname+'='+'http//'+thisip+':2380'
 print('promoted')
 cmdline=['name: '+thisname+'\n', 'data-dir: /var/lib/etcd\n', 'initial-advertise-peer-urls: http://'+thisip+':2380\n','listen-peer-urls: http://'+thisip+':2380\n','advertise-client-urls: http://'+thisip+':2379\n','listen-client-urls: http://'+thisip+':2379\n','initial-cluster: '+cluster+'\n','initial-cluster-state: '+cluster_state+'\n','initial-cluster-token: '+token+'\n']
 with open('/etc/etcd/etcd.conf.yml','w') as f:
  f.writelines(cmdline)
 etcfile.close()
else:
 cmdline=['./etcdput.py','possible'+myname, myip]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 

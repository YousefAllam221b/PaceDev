#!/bin/python3.6
# either to pass ips in separate comma then names in separate comma or to leave blank to use the internal hosts ip and name of this server
import subprocess,socket,sys
from time import sleep
token='token-01'
cluster_state='new'

this_host=socket.gethostbyname(socket.gethostname())
this_name=socket.gethostname()
try:
 hosts=[c for c in sys.argv[1].split(',')]
 names=[c for c in sys.argv[2].split(',')]
except:
 hosts=[str(this_host)]
 names=[str(this_name)]
cluster=''
hosnam=zip(names,hosts)
for x in hosnam:
 cluster+=x[0]+'=http://'+x[1]+':2380,' 
cmdline=['etcd','--data-dir=data.etcd','--name='+this_name,'--initial-advertise-peer-urls=http://'+this_host+':2380','--listen-peer-urls=http://'+this_host+':2380','--advertise-client-urls=http://'+this_host+':2379','--listen-client-urls=http://'+this_host+':2379','--initial-cluster='+cluster,'--initial-cluster-state='+cluster_state,'--initial-cluster-token='+token]
err = 2
while err == 2:
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 err = result.returncode
 if err == 2:
  sleep(2)

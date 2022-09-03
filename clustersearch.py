#!/bin/python3.6
import sys, subprocess
from etcdgetlocal import etcdget as getlocal

ip=sys.argv[1].split('.')
etcdserver='nohost'
serverstatus='nothing'
x=getlocal(sys.argv[1],'Active','--prefix')
for host in x:
 cmdline=['etcdctl','-w','json','--user=root:YN-Password_123','--endpoints='+host[1]+':2379','member','list']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 if result.returncode==0:
  etcdserver=host[1]
  serverstatus=result.stdout
serverstatus=str(serverstatus)[2:]
serverstatus=serverstatus[:-3]
if len(serverstatus) < 6:
 serverstatus='nothing'
else:
 etcdfile=open('/pacedata/runningetcdnodes.txt','w')
 etcdfile.write(serverstatus)
 etcdfile.close()
 etcdfile=open('/var/www/html/des20/Data/runningetcdnodes.txt','w')
 etcdfile.write(serverstatus)
 etcdfile.close()
print('hostis='+etcdserver)

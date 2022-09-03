#!/bin/python3.6
import sys, subprocess, os

os.environ['ETCDCTL_API']= '3'
ip=sys.argv[1]
cmdline=['etcdctl','--user=root:YN-Password_123','-w','json','--endpoints='+ip+':2379','member','list']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
serverstatus=result.stdout
serverstatus=str(serverstatus)[2:]
serverstatus=serverstatus[:-3]
etcdfile=open('/pacedata/runningetcdnodes.txt','w')
etcdfile.write(serverstatus)
etcdfile.close()
etcdfile=open('/var/www/html/des20/Data/runningetcdnodes.txt','w')
etcdfile.write(serverstatus)
etcdfile.close()
print(serverstatus)

#!/bin/python3.6
import subprocess,sys
import json
from time import sleep

endpoints=''
data=json.load(open('/pacedata/runningetcdnodes.txt'));
for x in data['members']:
 endpoints=endpoints+str(x['clientURLs'])[2:][:-2]
cmdline=['etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'endpoint','health']
err = 2
while err == 2:
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 err = result.returncode
 if err == 2:
  sleep(2)
print('result',result.stdout)
# cmdline=['etcdctl','-w','json','--endpoints='+host['addresses']['ipv4']+':2379','member','list','2>/dev/null']


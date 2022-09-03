#!/bin/python3.6
import subprocess,sys
from ast import literal_eval as mtuple
import json
endpoints=''
data=json.load(open('/pacedata/runningetcdnodes.txt'))
for x in data['members']:
 endpoints+=str(x['clientURLs'])[2:][:-2]
cmdline=['./etcdget.py','possible','--prefix']
possibleres=subprocess.run(cmdline,stdout=subprocess.PIPE)
possible=str(possibleres.stdout)[2:][:-3].split('\\n')
print('possible',possible)
for x in possible:
 print('x=',mtuple(x)[0], mtuple(x)[1])
 cmdline=['etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'del',mtuple(x)[0]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print('result=',result)
 cmdline=['etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'put','promote'+mtuple(x)[0].split('possible')[1],mtuple(x)[1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 cmdline=['etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'member','add',mtuple(x)[0].split('possible')[1],'--peer-urls=http://'+mtuple(x)[1]+':2380']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print(result)

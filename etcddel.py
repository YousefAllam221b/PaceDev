#!/bin/python3.6
import subprocess,sys, os
import json
from time import sleep

def etcddel(*args):
 os.environ['ETCDCTL_API']= '3'
 if args[-1]=='--prefix':
  pointer=-1
 else:
  pointer=0
 err = 2
 while err == 2:
  endpoints=''
  data=json.load(open('/pacedata/runningetcdnodes.txt'));
  for x in data['members']:
   endpoints=endpoints+str(x['clientURLs'])[2:][:-2]
  if len(args) > 1:
   cmdline=['etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'get',args[0],'--prefix']
  else:
   cmdline=['etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'get',args[0]]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  err = result.returncode
  if err == 2:
   from etcdget import etcdget as get
   get('any','any')
   sleep(1)
 mylist=str(result.stdout)[2:][:-3].split('\\n')
 zipped=zip(mylist[0::2],mylist[1::2])
 if mylist==['']:
  print('-1')
  return '-1'
 if len(args) > 1 and args[1] !='--prefix':
  todel=[]
  args2=args[1:]
  for x in args2:
   for y in zipped:
    if x in str(y):
     todel.append(y[0])
 else:
  todel=mylist
 if todel == []:
  print('-1')
  return (-1)
 count=0
 for key in todel:
  err = 2
  while err == 2:
   endpoints=''
   data=json.load(open('/pacedata/runningetcdnodes.txt'));
   for x in data['members']:
    endpoints=endpoints+str(x['clientURLs'])[2:][:-2]
   cmdline=['etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'del',key]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   err = result.returncode
   if err == 2:
    from etcdget import etcdget as get
    get('any','any')
    sleep(1)
  reslist=str(result.stdout)[2:][:-3]
  if '1' in reslist:
   count+=1
 print(count)
 

if __name__=='__main__':
 etcddel(*sys.argv[1:])

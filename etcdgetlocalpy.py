#!/bin/python3.6
import subprocess,sys, os
import json
from time import sleep

def etcdget(thehost,key, prefix=''):
 os.environ['ETCDCTL_API']= '3'
 z=[]
 endpoints=''
 endpoints='http://'+thehost+':2378'
 cmdline=['etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'get',key,prefix]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 z=[]
 try:
  if(prefix =='--prefix'):
   mylist=str(result.stdout)[2:][:-3].split('\\n')
   zipped=zip(mylist[0::2],mylist[1::2])
   for x in zipped:
    z.append(x) 
  elif(prefix == ''):
   z.append((str(result.stdout).split(key)[1][2:][:-3]))
  else:
   cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'get',key,'--prefix']
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   mylist=str(result.stdout)[2:][:-3].split('\\n')
   zipped=zip(mylist[0::2],mylist[1::2])
   for x in zipped:
    if prefix in str(x):
     z.append(x)
   if(len(z) == 0):
     z.append(-1)
 except:
  z.append(-1)
 return z

if __name__=='__main__':
 etcdget(*sys.argv[1:])

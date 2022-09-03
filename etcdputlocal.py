#!/bin/python3.6
import subprocess,sys, os
import json
from time import sleep

def etcdput(*args):
 os.environ['ETCDCTL_API']= '3'
 myip=args[0]
 key=args[1]
 val=args[2]
 endpoints=''
 endpoints='http://'+myip+':2378'
 cmdline=['etcdctl','--user=root:YN-Password_123','-w','json','--endpoints='+endpoints,'put',key,val]
 err = 2
 while err == 2:
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  err = result.returncode
  if err == 2:
    sleep(2)
 print(result)

if __name__=='__main__':
 etcdput(*sys.argv[1:])


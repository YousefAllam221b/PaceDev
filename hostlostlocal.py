#!/bin/python3.6
import subprocess,sys, os
from etcdget import etcdget as get
from etcdgethostrunning import etcdget as fastget
import json
from time import sleep
os.environ['ETCDCTL_API']= '3'

def looponhosts(leader,myhost, leaderip, myip):
 while True:
  sleep(1)
  if leader == myhost:
   continue
  res=fastget(leader,'--prefix') 
  print('theresult',res)
  if 'ok' not in res:
   cmdline='./leaderlost.sh '+leader+' '+myhost+' '+leaderip+' '+myip
   result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
   leaderinfo = get('leader','--prefix')[0]
   leader = leaderinfo[0].replace('leader/','')
   
   

if __name__=='__main__':
 '''
 leaderinfo = get('leader','--prefix')[0]
 leadername = leaderinfo[0].replace('leader/','')
 from socket import gethostname as hostname
 myhost = hostname()
 myip = get('known/'+myhost)[0] 
 leaderip = leaderinfo[1] 
 looponhosts(leadername, myhost, leaderip, myip)
 '''
 looponhosts('dhcp32570', 'dhcp10426', '10.11.11.245', '10.11.11.246')

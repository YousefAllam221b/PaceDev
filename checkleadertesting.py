#!/bin/python3.6
import subprocess,sys, os
import json
from time import sleep

def checkleader(key, prefix=''):
 os.environ['ETCDCTL_API']= '3'
 cmdline='./getmyip.sh'
 myip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
 print(myip)
 from etcdgetlocal import etcdget as getlocal
 leaderinfo = getlocal(myip,'leader','--prefix')[0]
 leader = leaderinfo[0].replace('leader/','')
 leaderip = leaderinfo[1]
 myhost = getlocal(myip,'ready/', myip)[0][0].replace('ready/','')
 print(leader, leaderip, myhost, myip)
 return
 exit()
 endpoints=''
 data=json.load(open('/pacedata/runningetcdnodes.txt'));
 for x in data['members']:
  endpoints=endpoints+str(x['clientURLs'])[2:][:-2]+','
 endpoints = endpoints[:-1]
 cmdline=['/bin/etcdctl','--user=root:YN-Password_123','--endpoints='+endpoints,'get',key,prefix]
 err = 2
 count = 0
 while count < 3: 
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  err = result.returncode
  if err == 2:
    count += 1
    sleep(1)
  else:
   return result 
 
 from etcdgetlocal import etcdget as getlocal
 cmdline='./getmyip.sh'
 myip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
 leaderinfo = getlocal(myip,'leader','--prefix')[0]
 leader = leaderinfo[0].replace('leader/','')
 leaderip = leaderinfo[1]
 myhost = getlocal(myip,'ready/', myip)[0][0].replace('ready/','')
 print(leader, leaderip, myhost, myip)
 return
 cmdline='./leaderlost.sh '+leader+' '+myhost+' '+leaderip+' '+myip
 result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
 return 'dead'

if __name__=='__main__':
 checkleader(*sys.argv[1:])

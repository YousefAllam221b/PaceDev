#!/bin/python3.6
import subprocess,sys, datetime
from logqueue import queuethis
from etcdput import etcdput as put 
from time import sleep
from etcdputlocal import etcdput as putlocal
from etcdget import etcdget as get 
from etcdgetlocal import etcdget as getlocal
from etcddel import etcddel as deli 
from etcddellocal import etcddel as delilocal 
from socket import gethostname as hostname
import logmsg
def setall(hostn,hostip,leader):
 with open('/pacedata/perfmon','r') as f:
  perfmon = f.readline()
 if '1' in perfmon:
  queuethis('Evacuate','running','system')
 myhost=hostname()
 cmdline=['/pace/getmyip.sh']
 myip=subprocess.run(cmdline,stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','')
 if myhost in hostn:
  if myhost in leader:
   cmdline=['/TopStor/Converttolocal.sh',myip]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/TopStor/resettarget.sh',myhost]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  delilocal(myip,"",hostn)
  while True:
   cmdline=['/TopStor/rebootme','reset']
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   sleep(10)
 else:
  if myhost in leader:
    print('iam here', hostn, hostip)
    cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    deli("",hostn)
  else:
    cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    delilocal(myip,"",hostn)
 logmsg.sendlog('Evacuaesu01','info','system',hostn)
 if '1' in perfmon:
  queuethis('Evacuate','stop','system')
 return

if __name__=='__main__':
 setall(*sys.argv[1:])

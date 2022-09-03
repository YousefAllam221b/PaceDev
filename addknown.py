#!/bin/python3.6
import socket, subprocess, logmsg
from etcddel import etcddel as etcddel
from deltolocal import deltolocal 
from logqueue import queuethis
from broadcast import broadcast as broadcast 
from broadcasttolocal import broadcasttolocal as broadcasttolocal
from etcdget import etcdget as get
from etcdgetlocal import etcdget as getlocal
from etcdput import etcdput as put 
from etcdputlocal import etcdput as putlocal 

myhost=socket.gethostname()
possible=get('possible','--prefix')
active = get('Active','--prefix')
for pos in possible:
 posname=pos[0].replace('possible','')
 if posname in str(active):
  print(posname)
  etcddel('lost',posname)
  etcddel('poss',posname)
  put('known/'+posname,pos[1])
allow=get('allowedPartners')
if 'notallowed' in str(allow):
 exit()
with open('/pacedata/perfmon','r') as f:
 perfmon = f.readline() 
queuethis('addknown','start','system')
possible=get('possible','--prefix')
print('possible=',possible)
if possible != []:
 for x in possible:
  print('x=',x[0], x[1])
  if 'yestoall' not in str(allow):
   print(x[0].replace('possible',''))
   print(str(allow))
   if x[0].replace('possible','') not in str(allow):
    print('iamhere')
    Active=get('AcivePartners','--prefix')
    if x[0].replace('possible','') not in str(Active):
     print('imhere2')
     queuethis('addknown','stop','system')
     exit()
  knowns=get('known','--prefix')
  putlocal(x[1],'configured/'+myhost,'yes')
  frstnode=get('frstnode')
  if frstnode == [-1]:
   frstnode = [""] 
  if x[0].replace('possible','') not in frstnode[0]:
   newfrstnode=frstnode[0]+'/'+x[0].replace('possible','')
   put('frstnode',newfrstnode)
  put('known/'+x[0].replace('possible',''),x[1])
  hostsubnet = getlocal(x[1],'hostipsubnet/'+x[0].replace('possible',''))[0]
  if hostsubnet == -1:
   hostsubnet = "24"
  etcddel('sync',x[0].replace('possible',''))
  etcddel('modified',x[0].replace('possible',''))
  deltolocal('sync',x[0].replace('possible',''))
  deltolocal('modified',x[0].replace('possible',''))
  put('ActivePartners/'+x[0].replace('possible',''),x[1])
  put('hostipsubnet/'+x[0].replace('possible',''),hostsubnet)
  put('configured/'+x[0].replace('possible',''),'yes')
  broadcasttolocal('hostipsubnet/'+x[0].replace('possible',''),hostsubnet)
  broadcasttolocal('ActivePartners/'+x[0].replace('possible',''),x[1])
  broadcasttolocal('configured/'+x[0].replace('possible',''),'yes')
  put('nextlead',x[0].replace('possible','')+'/'+x[1])
  broadcasttolocal('nextlead',x[0].replace('possible','')+'/'+x[1])
  cmdline=['/sbin/rabbitmqctl','add_user','rabb_'+x[0].replace('possible',''),'YousefNadody']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/sbin/rabbitmqctl','set_permissions','-p','/','rabb_'+x[0].replace('possible',''),'.*','.*','.*']
  etcddel('losthost/'+x[0].replace('possible',''))
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  put('change/'+x[0].replace('possible','')+'/booted',x[1])
  put('tosync','yes')
  broadcast('broadcast','/TopStor/pump.sh','syncnext.sh','nextlead','nextlead')
  if x[0].replace('possible','') in str(knowns):
   put('allowedPartners','notoall')
   etcddel('possible',x[0])
   logmsg.sendlog('AddHostsu01','info',arg[-1],name)
   queuethis('AddHost','stop',bargs[-1])
else:
 print('possible is empty')
queuethis('addknown.py','stop','system')

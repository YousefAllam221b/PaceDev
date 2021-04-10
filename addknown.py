#!/bin/python3.6
import subprocess, logmsg
from etcddel import etcddel as etcddel
from logqueue import queuethis
from broadcast import broadcast as broadcast 
from broadcasttolocal import broadcasttolocal as broadcasttolocal
from etcdget import etcdget as get
from etcdgetlocal import etcdget as getlocal
from etcdput import etcdput as put 
from etcdputlocal import etcdput as putlocal 
allow=get('allowedPartners')
if 'notallowed' in str(allow):
 exit()
with open('/pacedata/perfmon','r') as f:
 perfmon = f.readline() 
if '1' in perfmon:
 queuethis('addknown.py','start','system')
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
     exit()
  knowns=get('known','--prefix')
  putlocal(x[1],'configured','yes')
  frstnode=get('frstnode')
  if x[0].replace('possible','') not in frstnode[0]:
   newfrstnode=frstnode[0]+'/'+x[0].replace('possible','')
   put('frstnode',newfrstnode)
  put('known/'+x[0].replace('possible',''),x[1])
  put('ActivePartners/'+x[0].replace('possible',''),x[1])
  broadcasttolocal('ActivePartners/'+x[0].replace('possible',''),x[1])
  put('nextlead',x[0].replace('possible','')+'/'+x[1])
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
   queuethis('AddHost.py','stop',bargs[-1])
else:
 print('possible is empty')
if '1' in perfmon:
 queuethis('addknown.py','stop','system')

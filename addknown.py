#!/bin/python3.6
import subprocess,sys
from ast import literal_eval as mtuple
import json
endpoints=''
data=json.load(open('/pacedata/runningetcdnodes.txt'))
for x in data['members']:
 endpoints+=str(x['clientURLs'])[2:][:-2]
cmdline=['/pace/etcdget.py','possible','--prefix']
possibleres=subprocess.run(cmdline,stdout=subprocess.PIPE)
possible=str(possibleres.stdout)[2:][:-3].split('\\n')
print('possible=',possible)
if possible != ['']:
 for x in possible:
  print('x=',mtuple(x)[0], mtuple(x)[1])
  cmdline=['etcdctl','--endpoints='+endpoints,'del',mtuple(x)[0]]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  print('result=',result)
  cmdline=['etcdctl','--endpoints='+endpoints,'put','known/'+mtuple(x)[0].split('possible')[1],mtuple(x)[1]]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/sbin/rabbitmqctl','add_user','rabb_'+mtuple(x)[0].split('possible')[1],'YousefNadody']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/sbin/rabbitmqctl','set_permissions','-p','/','rabb_'+mtuple(x)[0].split('possible')[1],'".*"','".*"','".*"']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/TopStor/logmsg.sh','Partst01','info','system', mtuple(x)[0].split('possible')[1],mtuple(x)[1]]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  
  cmdline=['/pace/etcdput.py','change/'+mtuple(x)[0]+'/booted',mtuple(x)[1]]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/pace/iscsiwatchdog.sh','2>/dev/null']
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/bin/sleep','5']
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/pace/iscsiwatchdog.sh','2>/dev/null']
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/bin/sleep','5']
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/TopStor/logmsg.sh','Partsu01','info','system', mtuple(x)[0].split('possible')[1],mtuple(x)[1]]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
else:
 print('possible is empty')
cmdline=['/pace/etcdget.py','known','--prefix']
knownres=subprocess.run(cmdline,stdout=subprocess.PIPE)
known=str(knownres.stdout)[2:][:-3].replace('known/','').split('\\n')
print('known=',known)
if known != ['']:
 for kno in known:
  kn=mtuple(kno) 
  cmdline=['/pace/etcdgetlocal.py',str(kn[1]),'local','--prefix','2>/dev/null']
  heartres=subprocess.run(cmdline,stdout=subprocess.PIPE)
  heart=str(heartres.stdout)[2:][:-3].split('\\n')
  if(heart == ['-1']):
   cmdline=['/TopStor/logmsg.sh','Partst02','warning','system', str(kn[0])]
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/hostlost.sh',str(kn[0])]
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcddel.py','known/'+str(kn[0])]
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcddel.py','localrun/'+str(kn[0])]
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/bin/sleep','10']
   subprocess.run(cmdline,stdout=subprocess.PIPE)
  elif (mtuple(heart[0])[1] not in str(kn[1])):
   cmdline=['/pace/hostlost.sh',str(kn[0])]
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcddel.py','known/'+str(kn[0])]
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/pace/etcddel.py','localrun/'+str(kn[0])]
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/sbin/rabbitmqctl','delete_user','rabb_'+mtuple(x)[0].split('possible')[1],'YousefNadody']
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/bin/sleep','10']
   subprocess.run(cmdline,stdout=subprocess.PIPE)
   
 

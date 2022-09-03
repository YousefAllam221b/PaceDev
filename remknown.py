#!/bin/python3.6
import subprocess,sys, logmsg
from logqueue import queuethis
from etcddel import etcddel as etcddel
from etcdgetpy import etcdget as get
from etcdgetlocalpy import etcdget as getlocal
from time import time as stamp
from etcdput import etcdput as put 
from socket import gethostname as hostname

stamp = str(stamp())

def dosync(leader,*args):
  put(*args)
  put(args[0]+'/'+leader,args[1])
  return 

def remknown(leader,myhost):
 perfmon = '0'
# with open('/pacedata/perfmon','r') as f:
#  perfmon = f.readline() 
# if '1' in perfmon:
#  queuethis('remknown.py','start','system')
 known=get('known','--prefix')
 ready=get('ready','--prefix')
 nextone=get('nextlead/er')[0]
 knownchange = 0
 if len(ready) > len(known)+1:
  for r in ready:
   if r[0].split('/')[1] not in ( str(known) and str(leader)) :
    put('known/'+r[0].split('/')[1],r[1])
    dosync(leader,'sync/known/Add_'+r[0].split('/')[1]+'_'+r[1]+'/request','known_'+stamp)
    knownchange = 1
 if knownchange == 1:
  known=get('known','--prefix')
  
 if str(nextone) != '-1':
  if str(nextone[1]).split('/')[0] not in  str(known):
   etcddel('nextlead/er')
   nextone=[]
 if known != []:
  for kno in known:
   kn=kno 
   heart=getlocal(kn[1],'local','--prefix')
   if( '-1' in str(heart) or len(heart) < 1) or (heart[0][1] not in kn[1]):
    thelost = kn[0].split('/')[1]
    etcddel(kn[0])
    etcddel('host',thelost)
    etcddel('list',thelost)
    etcddel('sync/known','_'+thelost)
    dosync(leader,'sync/known/Del_known::_'+thelost+'/request','known_'+stamp)
    etcddel('sync/ready','_'+thelost)
    etcddel('sync/volumes','_'+thelost)
    etcddel('volumes',thelost)
    dosync(leader,'sync/volumes/request','volumes_'+stamp)
    etcddel('pools',thelost)
    etcddel('sync/pools','_'+thelost)
    dosync(leader,'sync/poolsnxt/Del_poolsnxt_'+thelost+'/request','poolsnxt_'+stamp)
    dosync(leader,'sync/pools/Del_pools_'+thelost+'/request','pools_'+stamp)
    etcddel('sync/nextlead',thelost)
    if kn[1] in str(nextone):
     etcddel('nextlead/er')
     dosync(leader,'sync/nextlead/Del_nextlead_--prefix/request','nextlead_'+stamp)
    logmsg.sendlog('Partst02','warning','system', kn[0].replace('known/',''))
    etcddel('ready/'+kn[0].replace('known/',''))
    dosync(leader,'sync/ready/Del_ready::_'+thelost+'/request','ready_'+stamp)
    etcddel('ipaddr',kn[0].replace('known/',''))
    print('hostlost ###########################################33333')
    #cmdline=['/pace/hostlost.sh',kn[0].replace('known/','')]
    #subprocess.run(cmdline,stdout=subprocess.PIPE)
    etcddel('localrun/'+str(kn[0]))
   else:
    if nextone == []:
     put('nextlead/er',kn[0].replace('known/','')+'/'+kn[1])
     dosync(leader,'sync/nextlead/Add_er_'+kn[0].split('/')[1]+'::'+kn[1]+'/request','nextlead_'+stamp)
     #etcddel('nextlead','--prefix')
 poss = get('pos','--prefix')
 if poss != []:
  for pos in poss:
   heart = getlocal(pos[1],'local','--prefix')
   if( '-1' in str(heart) or len(heart) < 1) or (heart[0][1] not in pos[1]):
    etcddel('ready/'+pos[0].replace('possible',''))
    dosync(leader,'sync/ready/Del_ready::_'+pos[0].replace('possible','')+'/request','ready_'+stamp)
    etcddel(pos[0])
   
   
 if '1' in perfmon:
  queuethis('remknown.py','stop','system')


if __name__=='__main__':
 if len(sys.argv) > 1:
  leader = sys.argv[1]
  myhost = sys.argv[2]
 else:
  leader=get('leader','--prefix')[0][0].split('/')[1]
  myhost = hostname()
 remknown(leader, myhost)

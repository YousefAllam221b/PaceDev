#!/bin/python3.6
import subprocess, sys
from logqueue import queuethis
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from broadcasttolocal import broadcasttolocal
from etcdputlocal import etcdput as putlocal 
from etcdgetlocal import etcdget as getlocal 
from Evacuatelocal import setall
from etcddel import etcddel as dels
from etcddellocal import etcddel as dellocal
from deltolocal import deltolocal
from usersyncall import usersyncall, oneusersync
from groupsyncall import groupsyncall, onegroupsync
from socket import gethostname as hostname
from etcdsync import synckeys
from time import time as timestamp

syncanitem = ['losthost','replipart','evacuatehost','Snapperiod', 'cron','user','group','tz','ntp','gw','dns' ]
forReceivers = [ 'user', 'group' ]
special1 = [ 'passwd' ]
wholeetcd = [ 'volumes', 'ipaddr' ]
etcdonly = [ 'cleanlost','balancedtype','sizevol', 'Partnr','ready','known','alias', 'hostipsubnet', 'namespace','leader','allowedPartners','activepool', 'poolsnxt','pools', 'localrun','logged','ActivePartners','configured','pool','nextlead']
syncs = etcdonly + syncanitem + special1 + wholeetcd
myhost = hostname()
##### sync request etcdonly template: sync/Operation/ADD/Del_oper1_oper2_../request Operation_stamp###########
##### sync request syncanitem with bash script: sync/Operation/commandline_oper1_oper2_../request Operation_stamp###########
##### sync request syncanitem with python script: sync/Operation/syncfn_commandline_oper1_oper2_../request Operation_stamp###########
##### synced template for request sync[0]/+node stamp #####################
##### initial sync for known nodes : sync/Operation/initial Operation_stamp #######################
##### synced template for initial sync for known nodes : sync/Operation/initial/node Operation_stamp #######################
##### delete request of same sync if ActivePartners qty reached #######################

def checksync(hostip='request',*args):
 synctypes[hostip](*args)

def syncinit(leader, myhost):
 global syncs, syncanitem, forReceivers, etcdonly, allsyncs
 stamp = int(timestamp() + 3600)
 for sync in syncs:
  put('sync/'+sync+'/'+'initial/request',sync+'_'+str(stamp)) 
  put('sync/'+sync+'/'+'initial/request/'+myhost,sync+'_'+str(stamp)) 
 return

def doinitsync(myip, syncinfo):
 global syncs, syncanitem, forReceivers, etcdonly, myhost, allsyncs
 from etctocron import etctocron 
 noinit = [ 'replipart' , 'evacuatehost' ]
 syncleft = syncinfo[0]
 stamp = syncinfo[1]
 sync = syncleft.split('/')[1]
 if sync in syncanitem and sync not in noinit:
    if 'cron' in sync:
     etctocron()
    if sync in 'user':
     print('syncing all users')
     usersyncall(myip) 
    if sync in 'group':
     print('syncing all groups')
     groupsyncall(myip)
    if sync in ['tz','ntp','gw','dns']: 
     cmdline='/TopStor/pump.sh HostManualconfig'+sync.upper()
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
 if sync in syncs:
  print('sycs',sync, myip)
  synckeys(myip, sync,sync)
     
 if sync not in syncs:
  print('there is a sync that is not defined:',sync)
  return 
 put(syncleft+'/'+myhost, stamp)
 synckeys(myip, syncleft, syncleft)

 return


def syncall(thisip,leader, myhost):
 global syncs, syncanitem, forReceivers, etcdonly, allsyncs
 myip = thisip
 allinitials = get('sync','initial')
 myinitials = [ x for x in allinitials if 'initial' in str(x)  and '/request/dhcp' not in str(x) ] 
 for syncinfo in myinitials:
   doinitsync(myip, syncinfo)

 allrequests = get('sync','--prefix')
 otherrequests = [ x for x in allrequests if '/request/dhcp' not in str(x) and 'initial' not in str(x) ] 
 
 for done in otherrequests:
      put(done[0]+'/'+myhost,done[1])
      synckeys(myip, done[0], done[0]) 


 return


def syncrequest(leader, myhost):
 global syncs, syncanitem, forReceivers, etcdonly,  allsyncs
 myip = get('ActivePartners/'+myhost)[0]
 allsyncs = get('sync','request') 
 donerequests = [ x for x in allsyncs if '/request/dhcp' in str(x) ] 
 mysyncs = [ x[1] for x in allsyncs if '/request/'+myhost in str(x) ] 
 myrequests = [ x for x in allsyncs if x[1] not in mysyncs  and '/request/dhcp' not in x[0] ] 
 myrequests.sort(key=lambda x: x[1].split('_')[1], reverse=False)
 print('myrequests', myrequests)
 for syncinfo in myrequests:
  if '/initial/' in str(syncinfo):
   if myhost != leader:
    doinitsync(myip, syncinfo)
  else:
   syncleft = syncinfo[0]
   stamp = syncinfo[1]
   sync = syncleft.split('/')[1]
   opers= syncleft.split('/')[2].split('_')
   if sync in wholeetcd :
    synckeys(myip, sync,sync)
   if sync in etcdonly and myhost != leader:
     if opers[0] == 'Add':
      if 'Split' in opers[1]:
       putlocal(myip,sync,opers[2].replace(':::','_').replace('::','/'))
      else:
       putlocal(myip,sync+'/'+opers[1].replace(':::','_').replace('::','/'),opers[2].replace(':::','_').replace('::','/'))
     else:
      print(sync,opers)
      dellocal(myip,opers[1].replace(':::','_').replace('::','/'),opers[2].replace(':::','_').replace('::','/'))
   if sync in syncanitem:
      if 'syncfn' in opers[0]:
       print('opers',opers)
       globals()[opers[1]](*opers[2:])
      else:
       cmdline='/TopStor/pump.sh '+opers[0]+' '+opers[1]
       result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
   if sync in special1 and myhost != leader :
      cmdline='/TopStor/'+opers[0]+' '+opers[1]+' '+opers[2]
      result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
      #cmdline='/TopStor/'+opers[0].split(':')[1]+' '+result+' '+opers[2] +' '+ opers[3]
      #result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
   if sync not in syncs:
    print('there is a sync that is not defined:',sync)
    return
   put(syncleft+'/'+myhost, stamp)
   if myhost != leader:
    putlocal(myip, syncleft+'/'+myhost, stamp)
    putlocal(myip, syncleft, stamp)
 if myhost != leader:
  dones = get('sync','/request/dhcp')
  otherdones = [ x for x in dones if '/request/dhcp' in str(x) ] 
  localdones = getlocal(myip, 'sync', '--prefix')
  for done in otherdones:
   if str(done) not in str(localdones):
    putlocal(myip, done[0],done[1])
    putlocal(myip, '/'.join(done[0].split('/')[:-1]), done[1])
  deleted = set()
  for done in localdones:
   if done[1] not in str(otherdones) and done[1] not in deleted:
    dellocal(myip, 'sync', done[1])
    deleted.add(done[1])
 return     


runcmd={'cron':'etctocron'} 
synctypes={'syncinit':syncinit, 'syncrequest':syncrequest, 'syncall':syncall }
if __name__=='__main__':
 if len(sys.argv) > 2: 
  leader = sys.argv[2]
  myhost = sys.argv[3]
 else:
  leader=get('leader','--prefix')[0][0].split('/')[1]
  myhost = hostname()
 
 synctypes[sys.argv[1]](leader, myhost)

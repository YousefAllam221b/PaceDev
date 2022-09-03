#!/bin/python3.6
import subprocess,sys
from etcdget import etcdget as get
from etcdgetlocal import etcdget as getlocal
from etcdput import etcdput as put
from broadcasttolocal import broadcasttolocal
from ast import literal_eval as mtuple
from socket import gethostname as hostname

myhost = hostname()
allusers= []

#def thread_add(*user):
def thread_add(user):
 username=user[0].replace('usersigroup/','')
 groupusers=user[1].split('/')[2]
 if groupusers=='no':
  groupusers='users'
 else:
  groupusers='users'+groupusers
 with open('/root/sync2','a') as f:
  f.write(str(user)+' + '+str(username)+', groupusers:'+groupusers+'\n')
 userigroup=user[1].split(':')
 userid=userigroup[0]
 usergd=userigroup[1]
 cmdline=['/TopStor/UnixAddGroup_sync',username,userid,usergd,groupusers]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)

#def thread_del(*user):
def thread_del(user):
 username=user[0].replace('usersigroup/','')
 if username not in str(allusers):
  print(username,str(allusers))
  cmdline=['/TopStor/UnixDelGroup_sync',username,'system']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def groupsyncall(hostip,tosync='usrsigroup'):
 global allusers
 global myusers
 global myip 
 myip=hostip
 allusers=get('usersigroup','--prefix')
 myusers=getlocal(myip,'usersigroup','--prefix')
 if tosync != 'usrsigroup':
  groups = get('modified','group')
  if -1 in groups:
   print('groups',groups)
   return
  groups = [ x[0].split('/')[2] for x in groups if myhost not in str(x) ]
  allusers = [ x for x in allusers if x[0].replace('usersigroup/','') ]
  delgroups = []
  leader=get('leader','--prefix')
  if myhost not in str(leader):
   for group in groups:
    if group not in allusers:
     delgroups.append(group)
  myusers= [ x for x in myusers if x[0].replace('usersinfo/','') in delgroups ]
 print(';;;;;',myusers,allusers)
 threads=[]
 if '-1' in allusers:
  allusers=[]
 if '-1' in myusers:
  myusers=[]
 for user in myusers:
  if user in allusers:
   print(user,allusers)
  else:
   thread_del(user)

 for user in allusers:
  thread_add(user)
 if tosync != 'usrsigroup': 
  for group in groups:
   gethosts = get('modified/group/'+group)[0]
   if myhost not in gethosts:
    put('modified/group/'+group,gethosts+'/'+myhost)
    broadcasttolocal('modified/group/'+group,gethosts+'/'+myhost)
 
 # thread_add(user)
#x=Thread(target=thread_add,name='addingusers',args=user)
#  x.start()
#  threads.append(x) 
#   x=Thread(target=thread_del,name='deletingusers',args=user)
#   x.start()
#   threads.append(x) 
# for tt in threads:
#  tt.join()
   
def onegroupsync(oper,usertosync):
 global allusers
 global myusers
 user=get('usersinfo', usertosync)[0]
 if oper == 'add':
  thread_add(user)
 else:
  thread_del(user)
 
  
if __name__=='__main__':
 with open('/root/sync2','w') as f:
  f.write('Starting\n')
 groupsyncall(*sys.argv[1:])

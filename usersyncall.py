#!/bin/python3.6
import subprocess,sys
from etcdget import etcdget as get
from etcdgetlocal import etcdget as getlocal
from etcdput import etcdput as put
from broadcasttolocal import broadcasttolocal
from ast import literal_eval as mtuple
from socket import gethostname as hostname

myhost = hostname()
allusers = []
def thread_add(user):
 username=user[0].replace('usersinfo/','')
 with open('/root/usersync2','w') as f:
  f.write(str(user)+' + '+str(username)+'\n')
 if username in str(myusers):
  userhashlocal=getlocal(myip,'usershash/'+username)[0]
  userhash=get('usershash/'+username)[0]
  if userhashlocal not in userhash:
   userinfo=user[1].split(':')
   userid=userinfo[0]
   usergd=userinfo[1]
   userhome=userinfo[2]
   cmdline=['/TopStor/UnixAddUser_sync',username,userhash,userid,usergd,userhome]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 else:
  userinfo=user[1].split(':')
  userid=userinfo[0]
  usergd=userinfo[1]
  userhash=get('usershash/'+username)[0]
  userhome=userinfo[2]
  cmdline=['/TopStor/UnixAddUser_sync',username,userhash,userid,usergd,userhome]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def thread_del(*user):
 global allusers
 username=user[0].replace('usersinfo/','')
 if username not in str(allusers):
  print(username,str(allusers))
  cmdline=['/TopStor/UnixDelUser_sync',username,'system']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def usersyncall(hostip,tosync='usersinfo'):
 global allusers
 global myusers
 global myip 
 myip = hostip
 allusers=get('usersinfo','--prefix')
 myusers=getlocal(myip,'usersinfo','--prefix')
 print(';;;;;;;;;;;;;;;;',myusers)
 if tosync != 'usersinfo': 
  users=get('modified','user')
  users = [ x for x in users if myhost not in str(x) ]
  users = [ x[0].split('/')[2] for x in users ]
  allusers = [ x for x in allusers if x[0].replace('usersinfo/','') in users]
  delusers = []
  for user in users:
   if user not in str(allusers):
    delusers.append(user)
  myusers= [ x for x in myusers if x[0].replace('usersinfo/','') in delusers ]
 threads=[]
 if '-1' in allusers:
  allusers=[]
 if '-1' in myusers:
  myusers=[]
 for user in allusers:
  thread_add(user)
 leader=get('leader','--prefix')
 if myhost not in str(leader):
  for user in myusers:
   if user in allusers:
    print(user,allusers)
   else:
    thread_del(user)
 if tosync != 'usersinfo': 
  for user in users:
   gethosts = get('modified/user/'+user)[0]
   if myhost not in gethosts:
    put('modified/user/'+user,gethosts+'/'+myhost)
    broadcasttolocal('modified/user/'+user,gethosts+'/'+myhost)
 
  
if __name__=='__main__':
 usersyncall(*sys.argv[1:])

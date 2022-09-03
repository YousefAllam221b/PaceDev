#!/bin/python3.6
from checkleader import checkleader
from remknown import remknown
from poolall import getall as getall
from sendhost import sendhost
import subprocess,sys, logmsg, os
from logqueue import queuethis
from etcddel import etcddel as etcddel
from etcdgetpy import etcdget as get
from etcdgetlocalpy import etcdget as getlocal
from time import time as stamp
from time import sleep
from etcdput import etcdput as put 
from socket import gethostname as hostname
from addknown import addknown
from putzpool import putzpool
from etcdputlocal import etcdput as putlocal 
from activeusers import activeusers
from addactive import addactive
from selectimport import selectimport
from zpooltoimport import zpooltoimport
from selectspare import spare2  
from checksyncs import syncrequest
from VolumeCheck import volumecheck
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor

os.environ['ETCDCTL_API']= '3'
myhost = hostname()
leaderinfo = checkleader('leader','--prefix').stdout.decode('utf-8').split('\n')
leader = leaderinfo[0].split('/')[1]
leaderip = leaderinfo[1]
 

def dosync(leader,*args):
  put(*args)
  put(args[0]+'/'+leader,args[1])
  return 

def iscsiwatchdogproc():
  cmdline='/pace/iscsiwatchdoglooper.sh'
  result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')

def fapiproc():
  cmdline='/pace/fapilooper.sh' 
  result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')

def putzpoolproc():
  global leader, myhost
  while True:
   try:
    putzpool(leader,myhost)
    sleep(5)
   except Exception as e:
    with open('/root/putzpoolerr','w') as f:
     f.write(e+'\n')

def addactiveproc():
  global leader, myhost
  while True:
   try:
    addactive(leader,myhost)
    sleep(5)
   except Exception as e:
    with open('/root/addactiveerr','w') as f:
     f.write(e+'\n')

def selectimportproc():
  global leader, myhost
  while True:
   try:
    allpools=get('pools/','--prefix')
    selectimport(myhost,allpools,leader)
    sleep(5)
   except Exception as e:
    with open('/root/selectimporterr','w') as f:
     f.write(e+'\n')
   

def zpooltoimportproc():
  global leader, myhost
  while True:
   try:
    zpooltoimport(leader, myhost)
    sleep(3)
   except Exception as e:
    print(e)
    with open('/root/zpooltoimporterr','w') as f:
     f.write(e+'\n')
 
def volumecheckproc():
  global leader, myhost
  while True:
   try:
    etcds = get('volumes','--prefix')
    replis = get('replivol','--prefix')
    cmdline = 'pcs resource'
    pcss = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8') 
    volumecheck(leader, myhost, etcds, replis, pcss)
    sleep(10)
   except Exception as e:
    print(volumecheck)
    with open('/root/volumecheckerr','w') as f:
     f.write(e+'\n')

def selectspareproc():
  global leader, myhost
  while True:
   try:
    spare2(leader, myhost)
    sleep(5)
   except Exception as e:
    with open('/root/selectsparerr','w') as f:

     f.write(e+'\n')

def syncrequestproc():
 global leader, myhost
 while True:
  try:
   syncrequest(leader, myhost)
   sleep(5)
  except Exception as e:
   with open('/root/syncrequesterr','w') as f:
    f.write(e+'\n')
 


def infinitproc():
 global leader, myhost
 leaderinfo = checkleader('leader','--prefix').stdout.decode('utf-8').split('\n')
 leader = leaderinfo[0].split('/')[1]
 leaderip = leaderinfo[1]
 cleader = leader
 myip = get('ActivePartners/'+myhost)[0]
 myalias = get('alias/'+myhost)[0]
 put('ready/'+myhost,myip)
 put('nextlead/er',myhost+'/'+myip)
 stampit = str(stamp())
 dosync(leader,'sync/ready/Add_'+myhost+'_'+myip+'/request','ready_'+stampit)
 dosync(leader,'sync/nextlead/Add_er_'+myhost+'::'+myip+'/request','ready_'+stampit)
 if myhost == cleader:
  logmsg.sendlog('Partsu03','info','system',myalias,myip)
 else:
  logmsg.sendlog('Partsu04','info','system',myalias,myip)
 
 while True:
  try:
   leaderinfo = checkleader('leader','--prefix').stdout.decode('utf-8').split('\n')
   leader = leaderinfo[0].split('/')[1]
   leaderip = leaderinfo[1]
   print('start remknown')
   remknown(leader,myhost) 
   print('finish remknown')
   if myhost == leader:
    addknown(leader,myhost)
   activeusers(leader, myhost)
  except Exception as e:
   with open('/root/infiniterr','w') as f:
    f.write(e+'\n')
   

loopers = [ infinitproc, iscsiwatchdogproc, fapiproc, putzpoolproc, addactiveproc, selectimportproc, zpooltoimportproc , volumecheckproc,
            selectspareproc , syncrequestproc ]
#loopers = [ syncrequestproc ]
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=len(loopers)) as e:
  res = [ e.submit(x) for x in loopers ] 
'''
 process = []
 for proc in loopers:
  p = Process(target=proc)
  p.start()
  process.append((proc,p))
 for proc in process:
  print('starting process:', proc[0])
  proc[1].join() 
'''

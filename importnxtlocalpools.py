#!/bin/python3.6
import sys,subprocess
from threading import Thread
from etcdgetlocal import etcdget as get
from etcdputlocal import etcdput as put
from etcddellocal import etcddel as dels
from ast import literal_eval as mtuple

def thread_run(*args):
 with open('/root/importlocal2','a') as f:
  f.write('\nargs1: '+str(args))
 print('local2:',args[1])
 subprocess.run(args,stdout=subprocess.PIPE)
 return


def importpools(*args):
 myip=args[0]
 myhost=args[1]
 thehost=args[2]
 threads=[]
 pool=""
 mypools=get(myip,'poolsnxt',myhost)
 if mypools[0] == -1:
  return
# with open('/TopStordata/forlocalpools') as f:
#  for line in f:
 print('mypools',myhost,thehost,mypools)
 if(len(mypools) < 1):
  return
 for line in mypools:
  with open('/root/importlocal','w') as f:
   f.write('poolline: '+str(line)+'\n')
  pool=line[0].split('/')[1]
  with open('/root/importlocal','a') as f:
   f.write('poolname: '+str(pool)+'\n')
  print('line', line)
  cmdline='/pace/Zpool2deadhostlocal '+myip+' '+thehost+' '+pool
  x=Thread(target=thread_run,name='importing-'+pool,args=cmdline.split(" "))
  x.start()
  threads.append(x) 
  for tt in threads:
   tt.join()
  
 return

if __name__ == "__main__":
 importpools(*sys.argv[1:])
 

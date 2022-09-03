#!/bin/python3.6
import subprocess,sys
from etcdget import etcdget as get
import json
def clearnamespace(*args):
 nslist=get('namespace','--prefix')
 ns=(x for x in nslist)
 for arg in args:
  try: 
   nsn=next(ns)
  except: 
   return
  cmdline='/sbin/ip addr del '+nsn[1]+' dev '+arg 
  subprocess.run(cmdline.split(),stdout=subprocess.PIPE)

if __name__=='__main__':
 clearnamespace(*sys.argv[1:])

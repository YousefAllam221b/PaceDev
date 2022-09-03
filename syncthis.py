#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from etcdputlocal import etcdput as putlocal 
from etcddellocal import etcddel as deli 

def syncthis(*args):
 knowns=[]
 knowninfo=get('known','--prefix')
 print('knwon',knowninfo)
 for k in knowninfo:
  deli(k[1],args[0],args[1])
  etcdinfo=get(args[0],args[1])
  print(args[0],args[1],etcdinfo)
  for item in etcdinfo:
   print('item',item[0],item[1],k[1])
   putlocal(k[1],item[0],item[1])

if __name__=='__main__':
 syncthis(*sys.argv[1:])

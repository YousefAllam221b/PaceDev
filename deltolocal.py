#!/bin/python3.6
import subprocess,sys, datetime, os
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from etcddellocal import etcddel as dellocal 

def deltolocal(*args):
 os.environ['ETCDCTL_API']= '3'
 knowns=[]
 knowninfo=get('known','--prefix')
 for k in knowninfo:
  print('param',k[1],*args)
  dellocal(k[1],*args)

if __name__=='__main__':
 deltolocal(*sys.argv[1:])

#!/bin/python3.6
import sys
from etcdget import etcdget as get
from etcdputlocal import etcdput as putlocal 
from etcddellocal import etcddel as dellocal 

def synckeys(thehost, key, tokey):
 print('thehost',thehost,tokey)
 mylist=get(key,'--prefix')
 dellocal(thehost,tokey,'--prefix')
 if '-1' in mylist:
  print('-1')
  exit()
 for item in mylist:
  moditem=""
  restitem=""
# if '/' in item[0]:
#  moditem=item[0].split('/')[0]
#  restitem='/'+item[0].replace(moditem+'/','')
  keysplit=item[0].split(key)
  if len(keysplit) > 1:
   restitem=keysplit[1]
  putlocal(thehost, tokey+restitem, item[1])

if __name__=='__main__':
 synckeys(*sys.argv[1:])

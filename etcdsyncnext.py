#!/bin/python3.6
import subprocess,sys
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from etcdputlocal import etcdputlocal


thehost=sys.argv[1]
key=sys.argv[2]
tokey=sys.argv[3]
result=get(key,'--prefix')
print("the result",result)
if result==[]:
 print('-1')
 exit(1)
for item in result:
 x=item[0].replace('/','')
 x=x.replace(str(key),'')
 if x =='':
   adding='';
 else:
   adding='/'+x
 etcdputlocal(thehost, tokey+adding, item[1])

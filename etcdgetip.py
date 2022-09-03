#!/bin/python3.6
import subprocess,sys
import json
from time import sleep

key=sys.argv[1]
endpoints=''
cmdline=['./etcdget.py','leader', '--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
if key in str(result.stdout):
 cmdline=['./etcdget.py','leader/'+key]
else:
 cmdline=['./etcdget.py','known/'+key]
err = 2
while err == 2:
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 err = result.returncode
 if err == 2:
  sleep(2)
print(str(result.stdout).split('known/')[0][2:][:-3])

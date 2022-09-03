#!/bin/python3.6
from etcdget import etcdget as get
import socket

myhost=socket.gethostname()
clients=get('ActivePartners','--prefix')
if myhost in str(clients):
 for c in clients:
  print('target/'+c[0].replace('ActivePartners/',''))

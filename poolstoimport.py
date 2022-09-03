#!/bin/python3.6
import subprocess, socket
from os import listdir
from logqueue import queuethis
from etcdput import etcdput as put
from etcdgetpy import etcdget as get 
from etcddel import etcddel as dels 
from os.path import getmtime

def getpoolstoimport():
 cmdline='/sbin/zpool import'
 result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
 pools = [ x.split(': ')[1] for x in result if 'pool: pdhcp' in x]
 return pools 

if __name__=='__main__':
 getpoolstoimport()

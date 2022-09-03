#!/bin/python3.6
import sys, os
os.environ['ETCDCTL_API']= '3'
  
def getraidrank(raid, removedisk, adddisk):
 ####raidraink = (name, location(0 is best), size (0) is best)
 raidrank = (0,0) 
 raidhosts = set()
 raiddsksize = adddisk['size']
 sizerank = 0
 for disk in (raid['disklist']+list([adddisk])):
  if disk['name'] == removedisk['name'] and disk['name'] != adddisk['name']:
   continue
  if ('F' or 'moved') in disk['changeop'] :
   continue
  raidhosts.add(disk['host'])
  if raiddsksize != disk['size']:
   sizerank = 1
 ###### ranking: no. of hosts differrence, and 1 for diff disk size found
 hostrank = len(raidhosts)-len(raid['disklist'])
 raid['raidrank'] = (hostrank, sizerank)
 return raid 

  
 
 
if __name__=='__main__':
 getraidrank(*sys.argv[1:])

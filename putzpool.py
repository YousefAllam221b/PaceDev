#!/bin/python3.6
import subprocess, json,sys
from socket import gethostname as hostname
from os import listdir
from logqueue import queuethis
from etcdput import etcdput as put
from etcdgetpy import etcdget as get 
from etcddel import etcddel as dels 
from os.path import getmtime

def putzpool(leader,myhost):
 perfmon = '0'
 #with open('/pacedata/perfmon','r') as f:
 # perfmon = f.readline() 
 #if '1' in perfmon:
 # queuethis('putzpool.py','start','system')
 #x=subprocess.check_output(['pgrep','-c','putzpool'])
 #x=str(x).replace("b'","").replace("'","").split('\\n')
 #if(x[0]!= '1' ):
 # print('process still running',x[0])
 #exit()

 sitechange=0
 readyhosts=get('ready','--prefix')
 knownpools=[f for f in listdir('/TopStordata/') if 'pdhcp' in f and 'pree' not in f ]
 cmdline='/sbin/zpool status'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 sty=str(result)[2:][:-3].replace('\\t','').split('\\n')
 cmdline='/bin/lsscsi -is'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 lsscsi=[x for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'LIO' in x ]
 freepool=[x for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'LIO' in x ]
 periods=get('Snapperiod','--prefix')
 raidtypes=['mirror','raidz','stripe']
 availraid=['mirror','raidz']
 raid2=['log','cache','spare']
 zpool=[]
 stripecount=0
 spaces=-2
 raidlist=[]
 disklist=[]
 lpools=[]
 ldisks=[]
 ldefdisks=[]
 linusedisks=[]
 lfreedisks=[]
 lsparedisks=[]
 lhosts=set()
 phosts=set()
 lraids=[]
 lvolumes=[]
 lsnapshots=[]
 poolsstatus=[]
 x=list(map(chr,(range(97,123))))
 cmdline=['fdisk','-l']
 cdisks=subprocess.run(cmdline,stderr=subprocess.PIPE, stdout=subprocess.PIPE)
 devs=cdisks.stdout.decode().split('Disk /dev/')
 drives = []
 for dev in devs:
  dsk = dev.split(':')[0]
  if 'sd' in dsk:
   drives.append(dsk) 
 cmdline=['/sbin/zfs','list','-t','snapshot,filesystem,volume','-o','name,creation,used,quota,usedbysnapshots,refcompressratio,prot:kind,available,referenced,status:mount,snap:type,partner:receiver,partner:sender','-H']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 zfslistall=str(result.stdout)[2:][:-3].replace('\\t',' ').split('\\n')
 #lists=[lpools,ldisks,ldefdisks,lavaildisks,lfreedisks,lsparedisks,lraids,lvolumes,lsnapshots]
 zfslistall=str(result.stdout)[2:][:-3].replace('\\t',' ').split('\\n')
 lists={'pools':lpools,'disks':ldisks,'defdisks':ldefdisks,'inusedisks':linusedisks,'freedisks':lfreedisks,'sparedisks':lsparedisks,'raids':lraids,'volumes':lvolumes,'snapshots':lsnapshots, 'hosts':list(lhosts), 'phosts':list(phosts)}
 for a in sty:
  #print('aaaaaa',a)
  b=a.split()
  if len(b) > 0:
   b.append(b[0])
   if any(drive in str(b[0]) for drive in drives):
    for lss in lsscsi:
     if any('/dev/'+b[0] in lss for drive in drives):
      b[0]='scsi-'+lss.split()[6]
      
  #print('strb',str(b))
  if "pdhc" in str(b) and  'pool' not in str(b):
   raidlist=[]
   volumelist=[]
   zdict={}
   rdict={}
   ddict={}
   zfslist=[x for x in zfslistall if b[0] in x ]
   #print('zfslist',b[0],zfslist)
   cmdline=['/sbin/zfs','get','avail:type',b[0], '-H']
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   availtype=str(result.stdout)[2:][:-3].split('\\t')[2]
   cmdline=['/sbin/zpool','list',b[0],'-H']
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   zlist=str(result.stdout)[2:][:-3].split('\\t')
   cmdline=['/sbin/zfs','get','compressratio','-H']
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   zlist2=str(result.stdout)[2:][:-3].split('\\t')
   if b[0] in knownpools:
    cachetime=getmtime('/TopStordata/'+b[0])
   else:
    cmdline='/sbin/zpool set cachefile=/TopStordata/'+b[0]+' '+b[0]
    subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
    cachetime='notset'
   #put('pools/'+b[0],myhost)
   poolsstatus.append(('pools/'+b[0],myhost))
   zdict={ 'name':b[0],'changeop':b[1], 'availtype':availtype, 'status':b[1],'host':myhost, 'used':str(zfslist[0].split()[6]),'available':str(zfslist[0].split()[11]), 'alloc': str(zlist[2]), 'size': zlist[1], 'empty': zlist[3], 'dedup': zlist[7], 'compressratio': zlist2[2],'timestamp':str(cachetime), 'raidlist': raidlist ,'volumes':volumelist}
   zpool.append(zdict)
   lpools.append(zdict) 
   for vol in zfslist:
    if b[0]+'/' in vol and '@' not in vol and b[0] in vol:
     volume=vol.split()
     volname=volume[0].split('/')[1]
     snaplist=[]
     snapperiod=[]
     snapperiod=[[x[0],x[1]] for x in periods if volname in x[0]]
     vdict={'fullname':volume[0],'name':volname, 'pool': b[0], 'host':myhost, 'creation':' '.join(volume[1:4]+volume[5:6]),'time':volume[4], 'used':volume[6], 'quota':volume[7], 'usedbysnapshots':volume[8], 'refcompressratio':volume[9], 'prot':volume[10],'available':volume[11], 'referenced':volume[12],'statusmount':volume[13], 'snapshots':snaplist, 'snapperiod':snapperiod}
     volumelist.append(vdict)
     lvolumes.append(vdict['name'])
    elif '@' in vol and b[0] in vol:
     snapshot=vol.split()
     snapname=snapshot[0].split('@')[1]
     partnerr=''
     partners=''
     if len(snapshot) >= 17:
      partners = snapshot[16]
     if len(snapshot) >= 16:
      partnerr = snapshot[15]
     sdict={'fullname':snapshot[0],'name':snapname, 'volume':volname, 'pool': b[0], 'host':myhost, 'creation':' '.join(snapshot[1:4]+volume[5:6]), 'time':snapshot[4], 'used':snapshot[6], 'quota':snapshot[7], 'usedbysnapshots':snapshot[8], 'refcompressratio':snapshot[9], 'prot':snapshot[10],'referenced':snapshot[12], 'statusmount':snapshot[13],'snaptype':snapshot[14], 'partnerR': partnerr, 'partnerS': partners}
     snaplist.append(sdict)
     lsnapshots.append(sdict['name'])
     
  elif any(raid in str(b) for raid in raidtypes):
   spaces=len(a.split(a.split()[0])[0])
   disklist=[]
   missingdisks=[0]
   if 'Availability' in zdict['availtype'] and 'stripe' in b[0]: 
    b[1] = 'DEGRADED' 
   rdict={ 'name':b[0], 'changeop':b[1],'status':b[1],'pool':zdict['name'],'host':myhost,'disklist':disklist, 'missingdisks':missingdisks }
   raidlist.append(rdict)
   lraids.append(rdict)
  elif any(raid in str(b) for raid in raid2):
   spaces=len(a.split(a.split()[0])[0])
   disklist=[]
   missingdisks=[0]
   b[1] = 'NA'
   if 'Availability' in zdict['availtype'] and raid not in availraids: 
    b[1] = 'DEGRADED' 
   rdict={ 'name':b[0], 'changeop':b[1],'status':b[1],'pool':zdict['name'],'host':myhost,'disklist':disklist, 'missingdisks':missingdisks }
   raidlist.append(rdict)
   lraids.append(rdict)
  elif 'dm-' in str(b) and 'corrupted' in str(b):
   missingdisks[0] += 1
    
  elif 'scsi' in str(b) or 'disk' in str(b) or '/dev/' in str(b) or (len(b) > 0 and 'sd' in b[0] and len(b[0]) < 5):
    diskid='-1'
    host='-1'
    size='-1' 
    devname='-1'
    disknotfound=1
    if  len(a.split('scsi')[0]) < (spaces+2) or (len(raidlist) < 1 and len(zpool)> 0):
     disklist=[]
     b[1] = 'NA'
     if 'Availability' in zdict['availtype'] : 
      b[1] = 'DEGRADED' 
     rdict={ 'name':'stripe-'+str(stripecount), 'pool':zdict['name'],'changeop':b[1],'status':b[1],'host':myhost,'disklist':disklist, 'missingdisks':[0] }
     raidlist.append(rdict)
     lraids.append(rdict)
     stripecount+=1
     disknotfound=1
    for lss in lsscsi:
     z=lss.split()
     if z[6] in b[0] and len(z[6]) > 3 and 'OFF' not in b[1] :
      diskid=lsscsi.index(lss)
      host=z[3].split('-')[1]
      lhosts.add(host)
      phosts.add(host)
      size=z[7]
      devname=z[5].replace('/dev/','')
      freepool.remove(lss)
      disknotfound=0
      break
    if disknotfound == 1:
      diskid=0
      host='-1'
      size='-1'
      devname=b[0]
      
     #else:
     # cmdline='/pace/hostlost.sh '+z[6]
     # subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
     
    if 'Availability' in zdict['availtype'] and 'DEGRAD' in rdict['changeop']:
     b[1] = 'ONLINE' 
    changeop=b[1]
    if host=='-1':
     raidlist[len(raidlist)-1]['changeop']='Warning'
     zpool[len(zpool)-1]['changeop']='Warning'
     changeop='Removed'
     sitechange=1
    ddict={'name':b[0],'actualdisk':b[-1], 'changeop':changeop,'pool':zdict['name'],'raid':rdict['name'],'status':b[1],'id': str(diskid), 'host':host, 'size':size,'devname':devname}
    disklist.append(ddict)
    ldisks.append(ddict)
 if len(freepool) > 0:
  raidlist=[]
  zdict={ 'name':'pree','changeop':'pree', 'available':'0', 'status':'pree', 'host':myhost,'used':'0', 'alloc': '0', 'empty': '0','size':'0', 'dedup': '0', 'compressratio': '0', 'raidlist': raidlist, 'volumes':[]}
  zpool.append(zdict)
  lpools.append(zdict)
  disklist=[]
  rdict={ 'name':'free', 'changeop':'free','status':'free','pool':'pree','host':myhost,'disklist':disklist, 'missingdisks':[0] }
  raidlist.append(rdict)
  lraids.append(rdict)
  for lss in freepool:
   z=lss.split()
   devname=z[5].replace('/dev/','')
   if devname not in drives:
    continue
   diskid=lsscsi.index(lss)
   host=z[3].split('-')[1]
   if host not in str(readyhosts):
    continue
 ##### commented for not adding free disks of freepool
   lhosts.add(host)
   size=z[7]
   ddict={'name':'scsi-'+z[6],'actualdisk':'scsi-'+z[6], 'changeop':'free','status':'free','raid':'free','pool':'pree','id': str(diskid), 'host':host, 'size':size,'devname':devname}
   if z[6] in str(zpool):
    continue
   disklist.append(ddict)
   ldisks.append(ddict)
 if len(lhosts)==0:
    lhosts.add('')
 if len(phosts)==0:
    phosts.add('')
 put('hosts/'+myhost+'/current',json.dumps(zpool))
 for disk in ldisks:
  if disk['changeop']=='free':
   lfreedisks.append(disk)
  elif disk['changeop'] =='AVAIL':
   lsparedisks.append(disk)
  elif disk['changeop'] != 'ONLINE': 
   ldefdisks.append(disk)
 put('lists/'+myhost,json.dumps(lists))
 xall=get('pools/','--prefix')
 x=[y for y in xall if myhost in str(y)]
 xnotfound=[y for y in x if y[0].replace('pools/','') not in str(poolsstatus)]
 xnew=[y for y in poolsstatus if y[0].replace('pools/','') not in str(x)]
 for y in xnotfound:
  if y[0] not in xall:
   dels(y[0].replace('pools/',''),'--prefix')
  else:
   dels(y[0])
 for y in xnew:
  put(y[0],y[1])
 if '1' in perfmon: 
  queuethis('putzpool.py','stop','system')
   
if __name__=='__main__':
 if len(sys.argv) > 1:
  leader = sys.argv[1]
  myhost = sys.argv[2]
 else:
  leader=get('leader','--prefix')[0][0].split('/')[1]
  myhost = hostname()
 putzpool(leader, myhost)

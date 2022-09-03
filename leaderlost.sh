#!/bin/sh
echo $@ > /root/leaderlost
cd /pace
leader=`echo $@ | awk '{print $1}'`
myhost=`echo $@ | awk '{print $2}'`
leaderip=`echo $@ | awk '{print $3}'`
myip=`echo $@ | awk '{print $4}'`
nextlead=`echo $@ | awk '{print $5}'`
nextleadip=`echo $@ | awk '{print $6}'`
enpdev='enp0s8'
rm -rf /etc/chrony.conf
cp /TopStor/chrony.conf /etc/
sed -i "s/MASTERSERVER/$nextleadip/g" /etc/chrony.conf
systemctl restart chronyd
 
echo $nextlead | grep $myhost
if [ $? -ne 0 ];
then
  echo leader is dead but another process was in the way to fix.  >> /root/zfspingtmp2
  echo leader is dead but another process was in the way to fix.
  sed -i "s/$leaderip/$nextleadip/g" /pacedata/runningetcdnodes.txt 2>/dev/null
# ETCDCTL_API=3 /pace/hostlostlocal.sh $leader $myip $leaderip
#   /pace/syncthtistoleader.py $myip pools/ $myhost
#   /pace/syncthtistoleader.py $myip volumes/ $myhost
#   /pace/etcdput.py ready/$myhost $myip
#   /pace/etcdput.py tosync/$myhost $myip
#   /TopStor/broadcast.py SyncHosts /TopStor/pump.sh addhost.py 
#   leaderall=` ./etcdget.py leader --prefix `
#   leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
#   leaderip=` ./etcdget.py leader/$leader `
  exit
fi
echo leader is dead..  > /root/zfspingtmp2
leaderfail=1
echo hi 
./etcdgetlocal.py $myip known --prefix | wc -l | grep 1
if [ $? -eq 0 ];
then
 /TopStor/logmsglocal.py $myip Partst05 info system $myhost &
fi
echo next lead is $nextleadip , $nextlead and this is me
echo $perfmon | grep 1
if [ $? -eq 0 ]; then
 /TopStor/logqueuelocal.py $myip AddingMePrimary start system 
fi
echo prepare the registry 
cho hostlostlocal getting all my pools from $leader >> /root/zfspingtmp2
#ETCDCTL_API=3 /pace/hostlostlocal.sh $leader $myip $leaderip
systemctl stop etcd 2>/dev/null
clusterip=`cat /pacedata/clusterip`
echo starting primary etcd with namespace >> /root/zfspingtmp2
./etccluster.py 'new' $myip 2>/dev/null
chmod +r /etc/etcd/etcd.conf.yml
systemctl daemon-reload 2>/dev/null
systemctl start etcd 2>/dev/null
ionice -c2 -n0 -p `pgrep etcd`
while true;
do
 echo starting etcd=$?
 systemctl status etcd
 if [ $? -eq 0 ];
 then
  break
 else
  sleep 1
 fi
done
echo adding me as a leader >> /root/zfspingtmpa2
 stamp=`date +%s%N`
./runningetcdnodes.py $myip 2>/dev/null
 /TopStor/logmsg.py Partst05 info system $myhost &
./etcdput.py ready/$myhost $myip  
/pace/etcdput.py sync/ready/Add_${myhost}_$myip/request ready_$stamp
./etcddel.py  leader --prefix  
./etcdput.py  leader/$myhost $myip 
/pace/etcdput.py sync/leader/Add_${myhost}_$myip/request leader_$stamp
./etcddel.py  host $leader  
./etcddel.py  known $myhost  
/pace/etcdput.py sync/known/Del_known_${myhost}/request known_$stamp
/TopStor/logmsg.py Partst02 warning system $leader 
#./broadcasttolocal.py sync/leader/$myhost $stamp 
./etcddel.py ipaddr $leader
./etcddel.py sync/ipaddr/$myhost  $stamp 
echo created namespaces >>/root/zfspingtmp2
./setnamespace.py $enpdev &
./setdataip.py &
echo importing all pools >> /root/zfspingtmp2
./etcddel.py toimport/$myhost &
toimport=1
#/sbin/zpool import -am &>/dev/null
echo running putzpool and nfs >> /root/zfspingtmp2
pgrep putzpool 
if [ $? -ne 0 ];
then
 /pace/putzpool.py 2 $isprimary $primtostd  &
 /TopStor/HostgetIPs
fi
 /pace/selectimport.py $myhost $myhost &
 /pace/zpooltoimport.py all 
 /pace/zpooltoimport.py all &
 /pace/selectspare.py $myhost &
pgrep activeusers 
if [ $? -ne 0 ];
then
 /pace/activeusers.py   &
fi
chgrp apache /var/www/html/des20/Data/* 2>/dev/null
chmod g+r /var/www/html/des20/Data/* 2>/dev/null
#else
# ETCDCTL_API=3 /pace/hostlostlocal.sh $leader $myip $leaderip
# systemctl stop etcd 2>/dev/null 
# echo starting waiting for new leader run >> /root/zfspingtmp2
# waiting=1
# result='nothing'
# while [ $waiting -eq 1 ]
# do
#  echo still looping for new leader run >> /root/zfspingtmp2
#  echo $result | grep nothing 
#  if [ $? -eq 0 ];
#  then
#   sleep 1 
#   result=`ETCDCTL_API=3 ./nodesearch.py $myip 2>/dev/null`
#  else
#   ./runningetcdnodes.py $myip 2>/dev/null
#   echo $perfmon | grep 1
#   if [ $? -eq 0 ]; then
#    /TopStor/logqueue.py AddingtoOtherleader start system 
#   fi
#   echo found the new leader run $result >> /root/zfspingtmp2
#   waiting=0
#   /pace/syncthtistoleader.py $myip pools/ $myhost
#   /pace/syncthtistoleader.py $myip volumes/ $myhost
#   /pace/etcdput.py ready/$myhost $myip
#   /pace/etcdput.py tosync/$myhost $myip
#   /TopStor/broadcast.py SyncHosts /TopStor/pump.sh addhost.py 
#   leaderall=` ./etcdget.py leader --prefix `
#   leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
#   leaderip=` ./etcdget.py leader/$leader `
#   rm -rf /etc/chrony.conf
#   cp /TopStor/chrony.conf /etc/
#   sed -i "s/MASTERSERVER/$leaderip/g" /etc/chrony.conf
#   systemctl restart chronyd
#   echo $perfmon | grep 1
#   if [ $? -eq 0 ]; then
#    /TopStor/logqueue.py AddingtoOtherleader start system 
#   fi
#  fi
# done 
# leader=`./etcdget.py leader --prefix | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
# continue
#fi
 

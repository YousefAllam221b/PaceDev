#!/usr/bin/sh
cd /pace
export ETCDCTL_API=3
ETCDCTL_API=3
echo $$ > /var/run/zfsping.pid
targetcli clearconfig True
targetcli saveconfig
targetcli restoreconfig /pacedata/targetconfig
targetcli iscsi/ delete iqn.2016-03.com.${myhost}:data
targetcli saveconfig
touch /pacedata/perfmon
#/TopStor/logqueueheap.py &
failddisks=''
oldlsscsi='00'
isknown=0
leaderfail=0
ActivePartners=1
partnersync=0
readycount=1
isprimary=0
primtostd=4
toimport=-1
clocker=0
oldclocker=0
clockdiff=0
date=`date`
enpdev='enp0s8'
systemctl restart target
cd /pace
rm -rf /pacedata/addiscsitargets 2>/dev/null
rm -rf /pacedata/startzfsping 2>/dev/null
/pace/startzfs.sh
leaderall=` ./etcdget.py leader --prefix `
leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
leadername=$leader
leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
date=`date `
myhost=`hostname -s`
myip=`/sbin/pcs resource show CC | grep Attributes | awk -F'ip=' '{print $2}' | awk '{print $1}'`
#./hostlostlocal.py $leadername $myhost $myip &
echo starting in $date >> /root/zfspingtmp
while true;
do
 leaderall=` ./etcdget.py leader --prefix `
 leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
 leadername=$leader
 leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
 pgrep fixpool 
 if [ $? -ne 0 ];
 then
  /TopStor/fixpool.py  &
 fi
 perfmon=`cat /pacedata/perfmon`
 needlocal=0
 runningcluster=0
 touch /var/www/html/des20/Data/TopStorqueue.log
 chown apache /var/www/html/des20/Data/TopStorqueue.log
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
 /TopStor/logqueue.py AmIprimary start system 
 fi
  
 echo check if I primary etcd >> /root/zfspingtmp
 netstat -ant | grep 2379 | grep LISTEN &>/dev/null
 if [ $? -eq 0 ]; 
 then
  echo I am primary etcd,isprimary:$isprimary, primtostd:$primtostd >> /root/zfspingtmp
  if [[ $isprimary -le 10 ]];
  then
   isprimary=$((isprimary+1))
  fi
  if [[ $primtostd -le 10 ]];
  then
   primtostd=$((primtostd+1))
  fi
  if [ $primtostd -eq 3 ];
  then
   /TopStor/logmsg.py Partsu05 info system $myhost
   primtostd=$((primtostd+1))
  fi
  if [ $isprimary -eq 3 ];
  then
   echo for $isprimary sending info Partsu03 booted with ip >> /root/zfspingtmp
   aliast='alias'
   myalias=`/pace/etcdget.py $aliast/$myhost`
   aliast='alias'
   /pace/etcdput.py ready/$myhost $myip
   /pace/etcdput.py $aliast/$myhost $myalias
   /pace/etcdput.py ActivePartners/$myhost $myip
   stamp=`date +%s`
   myalias=`echo $myalias | sed 's/\_/\:\:\:/g'`
   myalias=`echo $myalias | sed 's/\//\:\:\:/g'`
   /pace/etcdput.py sync/ActivePartners/Add_${myhost}_$myip/request ActivePartners_$stamp
   /pace/etcdput.py sync/ActivePartners/Add_${myhost}_$myip/request/$leadername ActivePartners_$stamp
   /pace/etcdput.py sync/$aliast/Add_${myhost}_$myalias/request/$leadername alias_$stamp
   /pace/etcdput.py sync/$aliast/Add_${myhost}_$myalias/request alias_$stamp
   /pace/etcdput.py sync/ready/Add_${myhost}_$myip/request ready_$stamp
   /pace/etcdput.py sync/ready/Add_${myhost}_$myip/request/$leadername ready_$stamp
   partnersync=0
   #/TopStor/broadcast.py SyncHosts /TopStor/pump.sh addhost.py 
   touch /pacedata/addiscsitargets 
   pgrep putzpool 
   if [ $? -ne 0 ];
   then
    /pace/putzpool.py 1 $isprimary $primtostd  &
   fi
   pgrep activeusers 
   if [ $? -ne 0 ];
   then
    /pace/activeusers.py   &
   fi

   ./etcddel.py toimport/$myhost
   toimport=2
  fi
  runningcluster=1
  echo checking leader record \(it should be me\)  >> /root/zfspingtmp
  leaderall=` ./etcdget.py leader --prefix 2>/dev/null`
  if [[ -z $leaderall ]]; 
  then
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
   /TopStor/logqueue.py FixIamleader start system 
 fi
   echo no leader although I am primary node >> /root/zfspingtmp
   ./runningetcdnodes.py $myip 2>/dev/null
   ./etcddel.py leader --prefix 2>/dev/null 
   ./etcdput.py leader/$myhost $myip 2>/dev/null 
   stamp=`date +%s`
    /pace/etcdput.py sync/leader/Add_${myhost}_$myip/request leader_$stamp
    /pace/etcdput.py sync/ready/Add_${myhost}_$myip/request/$myhost leader_$stamp
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
   /TopStor/logqueue.py FixIamleader stop system 
 fi
  fi
  echo adding known from list of possbiles >> /root/zfspingtmp
   pgrep  addknown 
   if [ $? -ne 0 ];
   then
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
    /TopStor/logqueue.py addingknown start system 
 fi
    ./addknown.py 2>/dev/null & 
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
    /TopStor/logqueue.py addingknown stop system 
 fi 
   fi
 echo checking if there are partners to sync >> /root/zfspingtmp
 else
  echo I am not a primary etcd.. heartbeating leader >> /root/zfspingtmp
  leaderall=` ./etcdget.py leader --prefix 2>&1`
  echo $leaderall | grep Error  &>/dev/null
  if [ $? -eq 0 ];
  then
   echo leader is dead..  >> /root/zfspingtmp
  else 
   echo I am not primary.. checking if I am local etcd>> /root/zfspingtmp
   netstat -ant | grep 2378 | grep $myip | grep LISTEN &>/dev/null
   if [ $? -ne 0 ];
   then
    echo I need to be local etcd .. no etcd is running>> /root/zfspingtmp
    needlocal=1
   else
    echo local etcd is already running>> /root/zfspingtmp
    needlocal=2
   fi
   echo checking if I am known host >> /root/zfspingtmp
   known=`./etcdget.py known --prefix`
   myconfig=` ./etcdgetlocal.py $myip configured/$myhost 2>/dev/null`
   echo $known | grep $myhost  &>/dev/null
   if [ $? -ne 0 ];
   then
    echo $myconfig | grep yes  &>/dev/null
    if [ $? -ne 0 ];
    then
     echo I am not a known and I am not configured. So, adding me as possible >> /root/zfspingtmp
     ./etcdput.py possible$myhost $myip 2>/dev/null &
    else
     echo I am not a known but I am configured so need to activate >> /root/zfspingtmp
     ./etcdput.py toactivate$myhost $myip 2>/dev/null &
    fi 
   else
   echo $perfmon | grep 1
   if [ $? -eq 0 ]; then
     /TopStor/logqueue.py iamkknown start system 
   fi
   echo I am known so running all needed etcd task:boradcast,isknown:$isknown >> /root/zfspingtmp
    if [[ $isknown -eq 0 ]];
    then
     echo running sendhost.py $leaderip 'user' 'recvreq' $myhost >>/root/tmp2
     leaderall=` ./etcdget.py leader --prefix `
     leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
     issync=`./etcdget.py sync initial | grep $myhost`initial
  echo $issync | grep $myhost
  if [ $? -eq 0 ];
  then
  ./checksyncs.py syncrequest
  else
   /pace/etcddellocal.py $myip sync --prefix
   /pace/checksyncs.py syncall $myip 
   syncinit=$myhost
  fi 
     leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
     ./checksync.py syncrequest
     /pace/sendhost.py $leaderip 'logall' 'recvreq' $myhost 
     isknown=$((isknown+1))
    fi
    if [[ $isknown -le 10 ]];
    then
     isknown=$((isknown+1))
    fi
    if [[ $isknown -eq 3 ]];
    then
     issync=`./etcdgetlocal.py $myip sync initial`initial
     echo $issync | grep $myhost
     if [ $? -eq 0 ]
     then
      echo syncrequests only 
      ./checksyncs.py syncrequest
     else
      echo have to syncall 
      ./checksyncs.py syncall $myip
     fi 
     stamp=`date +%s`
     /pace/etcdput.py ready/$myhost $myip 
     /pace/etcdput.py ActivePartners/$myhost $myip 
     /pace/etcdput.py sync/ActivePartners/Add_${myhost}_$myip/request/$leadername ActivePartners_$stamp
     /pace/etcdput.py sync/ActivePartners/Add_${myhost}_$myip/request ActivePartners_$stamp
     /pace/etcdput.py sync/ready/Add_${myhost}_$myip/request/$leadername ready_$stamp
     /pace/etcdput.py sync/ready/Add_${myhost}_$myip/request ready_$stamp

     /TopStor/broadcast.py SyncHosts /TopStor/pump.sh addhost.py
     #targetcli clearconfig True
     #targetcli saveconfig
     #targetcli restoreconfig /pacedata/targetconfig
     touch /pacedata/addiscsitargets 
   ./etcddel.py toimport/$myhost &
     toimport=1
    fi
    echo finish running tasks task:boradcast, log..etc >> /root/zfspingtmp
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
    /TopStor/logqueue.py iamkknown stop system 
 fi
   fi
  fi 
 fi
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
 /TopStor/logqueue.py AmIprimary stop system 
 fi
 pgrep putzpool 
 if [ $? -ne 0 ];
 then
  /pace/putzpool.py 3 $isprimary $primtostd  &
 fi
 pgrep activeusers 
 if [ $? -ne 0 ];
 then
  /pace/activeusers.py   &
 fi


 echo checking if I need to run local etcd >> /root/zfspingtmp
 if [[ $needlocal -eq 1 ]];
 then
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
  /TopStor/logqueue.py IamLocal start system 
 fi
  echo start the local etcd >> /root/zfspingtmp
  ./etccluster.py 'local' $myip 2>/dev/null
  chmod +r /etc/etcd/etcd.conf.yml
  systemctl daemon-reload
  systemctl stop etcd 2>/dev/null
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
  leaderall=` ./etcdget.py leader --prefix `
  leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
  leadername=$leader
  leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
  ./etcdsync.py $myip primary primary 2>/dev/null &
  ./etcddellocal.py $myip known --prefix 2>/dev/null &
  ./etcddellocal.py $myip localrun --prefix 2>/dev/null &
  ./etcddellocal.py $myip run --prefix 2>/dev/null &
  ./etcdsync.py $myip known known 2>/dev/null &
  #./etcdsync.py $myip localrun localrun 2>/dev/null &
  ./etcdsync.py $myip leader leader 2>/dev/null &
  echo /TopStor/syncq.py $leaderip $myhost >>/root/tmp2
  /TopStor/syncq.py $leaderip $myhost 2>/root/syncqerror
#   ./etcddellocal.py $myip known/$myhost --prefix 2>/dev/null
  echo done and exit >> /root/zfspingtmp
  continue 
 echo $perfmon | grep 1
 if [ $? -eq 0 ]; then
  /TopStor/logqueue.py IamLocal stop system 
 fi
 fi
 if [[ $needlocal -eq  2 ]];
 then
  echo I am already local etcd running iscsirefresh on $myip $myhost  >> /root/zfspingtmp
  pgrep fapi 
  if [ $? -ne 0 ];
  then
   cd /TopStor
   ./fapi.py 1>/root/fapi.log 2>/root/fapierr.log &
  fi
  pgrep iscsiwatchdog
  if [ $? -ne 0 ];
  then
   /pace/iscsiwatchdog.sh $myip $myhost $leader 2>/dev/null &
  fi
  pgrep checksyncs 
  if [ $? -ne 0 ];
  then
   /pace/checksyncs.py syncrequest
  fi

 fi
 echo checking if still in the start initcron is still running  >> /root/zfspingtmp
 if [ -f /pacedata/forzfsping ];
 then
  echo Yes. so I have to exit >> /root/zfspingtmp
  continue
 fi
 cd /pace
 echo Checking  I am primary >> /root/zfspingtmp
 if [[ $runningcluster -eq 1 ]];
 then
  echo Yes I am primary so will check for known hosts >> /root/zfspingtmp
   pgrep  remknown 
   if [ $? -ne 0 ];
   then
    ./remknown.py $myhost 2>/dev/null & 
   fi
   pgrep  addknown 
   if [ $? -ne 0 ];
   then
    ./addknown.py $myhost 2>/dev/null & 
   fi
   pgrep addactive 
   if [ $? -ne 0 ];
   then
    ./addactive.py $myhost 2>/dev/null & 
   fi
   pgrep  selectimport 
   if [ $? -ne 0 ];
   then
    stamp=`date +%s`
    /TopStor/selectimport.py $myhost $leader &
   fi
 fi 
 echo toimport = $toimport >> /root/zfspingtmp
 
 if [ $toimport -gt 0 ];
 then
  ETCDCTL_API=3 /pace/etcdget.py toimport/$myhost 
  mytoimport=`ETCDCTL_API=3 /pace/etcdget.py toimport/$myhost`
  if [ $mytoimport == '-1' ]; then 
   echo Yes  I have no record in toimport/$myhost even no nothing=$mytoimport >> /root/zfspingtmp
  fi
  echo $mytoimport | grep nothing
  if [ $? -eq 0 ];
  then
   echo it is nothing , toimport=$toimport >> /root/zfspingtmp
   if [ $toimport -eq 1 ];
   then
    if [ $leaderfail -eq 0 ];
    then
     /TopStor/logmsg.py Partsu04 info system $myhost $myip &
     ./etcddel.py cann --prefix 2>/dev/null &
    else
     leaderfail=0
    fi
   fi
   if [ $toimport -eq 2 ];
   then
    if [ $leaderfail -eq 0 ];
    then
     /TopStor/logmsg.py Partsu03 info system $myhost $myip &
     ./etcddel.py cann --prefix 2>/dev/null &
    else
     leaderfail=0
    fi
     
   fi
   if [ $toimport -eq 3 ];
   then
    /TopStor/logmsg.py Partsu06 info system &
   fi
   toimport=0
   oldclocker=$clocker
  else
   echo checking zpool to import>> /root/zfspingtmp
   lsscsi=`lsscsi | wc -c`'lsscsi'
   pgrep zpooltoimport
   if [ $? -ne 0 ];
   then
    /TopStor/zpooltoimport.py all 2>/dev/null &  
    oldlsscsi=$lsscsi
   fi
   pgrep  VolumeCheck 
   if [ $? -ne 0 ];
   then
    /TopStor/VolumeCheck.py
   fi
  fi
 fi
 if [ $toimport -eq 0 ];
 then
  clocker=`date +%s`
  clockdiff=$((clocker-oldclocker))
 fi
 echo Clockdiff = $clockdiff >> /root/zfspingtmp
 if [ $clockdiff -ge 500 ];
 then
  ./etcddel.py toimport/$myhost &
  /TopStor/logmsg.py Partst06 info system  &
  toimport=3
  oldclocker=$clocker
  clockdiff=0
 fi
 pgrep fapi 
 if [ $? -ne 0 ];
 then
  cd /TopStor
  ./fapi.py 1>/root/fapi.log 2>/root/fapierr.log &
 fi
 pgrep iscsiwatchdog
 if [ $? -ne 0 ];
 then
  /pace/iscsiwatchdog.sh 2>/dev/null  &
 fi
 pgrep checksyncs 
 if [ $? -ne 0 ];
 then
  /pace/checksyncs.py syncrequest
 fi

  echo Collecting a change in system occured >> /root/zfspingtmp
 #/pace/changeop.py hosts/$myhost/current d
   pgrep  changeop 
   if [ $? -ne 0 ];
   then
    ETCDCTL_API=3 /pace/changeop.py $myhost &
   fi

   pgrep  selectspare 
   if [ $? -ne 0 ];
   then
    ETCDCTL_API=3 /pace/selectspare.py $myhost &
   fi
    /TopStor/electspare.py 
done

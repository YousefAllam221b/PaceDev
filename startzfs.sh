#!/bin/sh
cd /pace
export ETCDCTL_API=3
echo >/etc/exports
echo finish > /TopStordata/rebootstatus
/sbin/pcs resource disable namespaces  2>/dev/null
/sbin/pcs resource disable  ip-all  2>/dev/null
/sbin/pcs resource disable  dataip  2>/dev/null
/sbin/zpool export -a 2>/dev/null
aliast='alias'
#yes | cp /TopStor/smb.conf /etc/samba/
#yes | cp /TopStor/exports /etc/
ln -f /etc/passwd  /opt/passwds/passwd
ln -f /etc/group  /opt/passwds/group
ln -f /etc/shadow  /opt/passwds/shadow
echo starting startzfs > /root/tmp2
#systemctl start smb &
iscsimapping='/pacedata/iscsimapping';
runningpools='/pacedata/pools/runningpools';
enpdev='enp0s8'
myhost=`hostname -s`
#/sbin/rabbitmqctl add_user rabbmezo HIHIHI 2>/dev/null
#/sbin/rabbitmqctl set_permissions -p / rabbmezo ".*" ".*" ".*" 2>/dev/null
#/sbin/rabbitmqctl set_user_tags rabbmezo administrator
myip=`/sbin/pcs resource show CC | grep Attributes | awk -F'ip=' '{print $2}' | awk '{print $1}'`
ccnic=`/sbin/pcs resource show CC | grep nic\= | awk -F'nic=' '{print $2}' | awk '{print $1}'`
/sbin/pcs resource delete --force namespaces  2>/dev/null
/sbin/pcs resource delete --force ip-all  2>/dev/null
/sbin/pcs resource delete --force dataip  2>/dev/null
echo starting etcd as local >>/root/tmp2
./etccluster.py 'local' $myip 2>/dev/null
chmod +r /etc/etcd/etcd.conf.yml 2>/dev/null
systemctl daemon-reload 2>/dev/null
systemctl stop etcd 2>/dev/null
sleep 2
systemctl start etcd 2>/dev/null
while true;
   do
    echo starting etcd=$?
    systemctl status etcd
    if [ $? -eq 0 ];
    then
     break
    else
     systemctl start etcd
     sleep 2
    fi
done
cat /pacedata/initetcd | grep 1
if [ $? -ne 0 ];
then
 /pace/etcdcmdlocal.py $myip user add root:YN-Password_123
 /pace/etcdcmdlocal.py $myip auth enable
 echo 1 > /pacedata/initetcd
fi
datenow=`date +%m/%d/%Y`; timenow=`date +%T`;
knownsearch=0
result='nohost'
./etcdputlocal.py $myip ActivePartners/$myhost $myip
toreset=`./etcdgetlocal.py $myip toreset`'r'
echo $toreset | grep yes
if [ $? -eq 0 ];
then
 #./etcddellocal.py $myip "" --prefix
 ./etcdputlocal.py $myip configured/$myhost yes
 ./etcddellocal.py $myip request --prefix 2>/dev/null 
 targetcli clearconfig confirm=true
 /TopStor/logmsg2.sh $datenow $timenow $myhost Evacuaesu01 info system $myhost
else
 result=` ETCDCTL_API=3 ./clustersearch.py $myip 2>/dev/null | grep hostis | awk -F'=' '{print $2}'`
fi
echo $result | grep nohost 
if [ $? -ne 0 ];
then
 echo found cluster with leader $result.. no need for node search >>/root/tmp2
 knownsearch=1
else
 configured=`./etcdgetlocal.py $myip configured/$myhost` 
 echo configured is $configured >>/root/tmp2
 systemctl stop etcd 
 echo $configured | grep no 
 if [ $? -ne 0 ];
 then
  echo configured is $configured so result will not search for a primary>>/root/tmp2
  result='nothing'
 else
  echo starting nodesearch>>/root/tmp2
  result=` ETCDCTL_API=3 ./nodesearch.sh $myip 2>/dev/null`
  echo finish nodesearch with ip=$myip, result=$result >>/root/tmp2
 fi
fi
freshcluster=0
echo $result > /root/hihi
echo myip=$myip >> /root/hihi
echo $result | grep nothing 
if [ $? -eq 0 ];
then
 echo no node is found so making me as primary>>/root/tmp2
 rm -rf /pacedata/running*
 freshcluster=1
  ./etccluster.py 'new' $myip 2>/dev/null
 chmod +r /etc/etcd/etcd.conf.yml 2>/dev/null
 echo startinetcd >>/root/tmp2
 systemctl daemon-reload 2>/dev/null
 systemctl stop etcd
 sleep 2
 systemctl start etcd >> /root/tmp2 
 while true;
 do
  echo starting etcd=$?
  systemctl status etcd
  if [ $? -eq 0 ];
  then
   break
  else
   systemctl start etcd >> /root/tmp2
   sleep 2 
  fi
 done
 echo started etcd as primary>>/root/tmp2
 echo started etcd as primary
 datenow=`date +%m/%d/%Y`; timenow=`date +%T`;
 /pace/etcdcmd.py user add root:YN-Password_123
 /pace/etcdcmd.py auth enable
 ./runningetcdnodes.py $myip 2>/dev/null
 echo check syncinit 
 issync=`./etcdget.py sync initial`
 echo $issync | grep '\-1' 
 if [ $? -eq 0 ];
 then
  ./checksyncs.py syncinit
 fi
 #./etcddel.py sync --prefix
 ./etcddel.py needtoreplace --prefix
 ./etcddel.py needtoimport --prefix
 ./etcddel.py known --prefix 2>/dev/null 
 /TopStor/HostManualconfigTZ $myip 
 /TopStor/HostManualconfigNTP $myip
 cd /pace
 ./etcddel.py OpenTasks --prefix
 ./etcddel.py cpu --prefix
 ./etcddel.py pool --prefix
 ./etcdget.py configured/$myhost | grep 1
 if [ $? -eq 0 ];
 then
  ./etcdput.py configured/$myhost yes 
 else 
  ./etcdget.py frstnode | grep dhcp
  if [ $? -ne 0 ];
  then
   ./etcdput.py frstnode $myhost
  fi
 fi
 gateway=`ETCDCTL_API=3 /TopStor/etcdget.py gw/$myhost`
 echo $gateway | grep '\.'
 if [ $? -eq 0 ];
 then
  route del default
  route add default gw $gateway
 fi 
 /TopStor/HostManualconfigDNS
 tzone=`ETCDCTL_API=3 /TopStor/etcdget.py tz/$myhost`
 echo $tzone | grep '\/'
 if [ $? -ne 0 ];
 then
  tzone='@@'`timedatectl | grep  zone | awk -F':' '{print $2}'` 
  tzone=${tzone//,/@}
  tzone=${tzone// /_}
#  ./etcdput.py tz $tzone
 fi
 ntp=`ETCDCTL_API=3 /TopStor/etcdget.py ntp/$myhost`
 echo ntp=$ntp >/root/ntptemp
 rm -rf /etc/chrony.conf
 cp /TopStor/chrony.conf /etc/
 echo $ntp | grep '\.'
 if [ $? -eq 0 ];
 then
  sed -i "s/MASTERSERVER/$ntp/g" /etc/chrony.conf
 else
  sed -i '/MASTERSERVER/,+1 d' /etc/chrony.conf
  ntp=`cat /etc/chrony.conf | grep server | grep -v servers | head -1 | awk '{print $2}'`
  ./etcdgput.py ntp $ntp
 fi
 systemctl restart chronyd
 /TopStor/logmsg2.sh $datenow $timenow $myhost Partst03 info system $myhost $myip
 ./etcddel.py possbile --prefix 2>/dev/null 
 ./etcddel.py ready --prefix 2>/dev/null 
 ./etcddel.py locked --prefix 2>/dev/null 
 ./etcddel.py cannot --prefix 2>/dev/null 
 ./etcddel.py request --prefix 2>/dev/null 
 ./etcddel.py connections --prefix 2>/dev/null 
 allow=`ETCDCTL_API=3 ./etcdget.py allowedPartners ` 2>/dev/null 
 echo checking allow=$allow >>/root/tmp2
 echo $allow | grep 1
 if [ $? -eq 0 ];
 then
  ./etcdput.py allowedPartners notallowed 
  echo started setting allowedPartners to allow >>/root/tmp2
 fi 
 myalias=`ETCDCTL_API=3 /pace/etcdget.py $aliast/$myhost`
 if [[ $myalias -eq -1 ]];
 then
   /pace/etcdput.py $aliast/$myhost $myhost
 fi
 rm -rf /var/lib/iscsi/nodes/* 2>/dev/null
 echo creating namespaces >>/root/tmp2
 ./setnamespace.py $enpdev
 ./setdataip.py
 echo created namespaces >>/root/tmp2
 ./etcddel.py versions --prefix
 cversion=`git branch | grep '*' | awk -F'QS' '{print $2}'`
 ./etcdput.py versions/$myhost $cversion
 ./etcddel.py leader --prefix 2>/dev/null
 ./etcddel.py pools --prefix 2>/dev/null
 ./etcddel.py poolsnxt --prefix 2>/dev/null
 ./etcddel.py cann --prefix 2>/dev/null
 ./etcddel.py prop --prefix 2>/dev/null
 ./etcddel.py Snapperiod --prefix 2>/dev/null
 ./etcdput.py leader/$myhost $myip 2>/dev/null
 ./etcdput.py primary/name $myhost 2>/dev/null
 ./etcdput.py primary/address $myip 2>/dev/null
 ./etcddel.py known --prefix 2>/dev/null
 ./etcddel.py possible --prefix 2>/dev/null
 ./etcddel.py localrun --prefix 2>/dev/null
 ./etcddel.py to  --prefix 2>/dev/null
 ./etcddel.py hosts  --prefix 2>/dev/null
 ./etcddel.py oldhosts  --prefix 2>/dev/null
 ./etcddel.py vol  --prefix 2>/dev/null
 ./etcddel.py ipaddr  --prefix 2>/dev/null
 ./etcddel.py active --prefix 2>/dev/null
 ./etcddel.py sync/volumes --prefix 2>/dev/null
 systemctl start iscsid &
 systemctl start iscsi &
 systemctl start topstorremote
 systemctl start topstorremoteack
 systemctl start servicewatchdog 
 gateway=`ETCDCTL_API=3 /TopStor/etcdget.py gw/$myhost`
 oldgw=`ip route |grep default | awk '{print $3}'`
 echo $gateway | grep '\.'
 if [ $? -eq 0 ];
 then
  route del default gw $oldgw
  route add default gw $gateway
 else
   ./etcdput.py gw/$myhost $oldgw
 fi 
 dnsname=`ETCDCTL_API=3 /TopStor/etcdget.py dnsname/$myhost`
 dnssearch=`ETCDCTL_API=3 /TopStor/etcdget.py dnssearch/$myhost`
 echo $dnsname | grep '\-1'
 if [ $? -eq 0 ];
 then
  dnsname=`cat /etc/resolv.conf | grep name | head -1 | awk '{print $2}'`
 ./etcdput.py dnsname/$myhost $dnsname 
 fi
 echo $dnssearch | grep '\-1'
 if [ $? -eq 0 ];
 then
  dnssearch=`cat /etc/resolv.conf | grep search | head -1 | awk '{print $2}'`
  ./etcdput.py dnssearch/$myhost $dnssearch 
 fi
 /TopStor/HostManualconfigDNS 
 cat /etc/passwd | grep NoUser 
 if [ $? -ne 0 ];
 then
  /TopStor/UnixAddUser NoUser NoHome groupsnull 1234567890YosuefNadody NoHome 1G admin
 fi
 cat /etc/passwd | grep Everyone
 if [ $? -ne 0 ];
 then
  /TopStor/UnixAddGroup Everyone usersNoUser admin
 fi
 /sbin/zpool export -a 2>/dev/null
 rm -rf /pdhcp*
 /TopStor/crontoetc.py all &
 echo startiscsiwatchdog >>/root/tmp2
 /pace/iscsiwatchdog.sh 2>/dev/null
 echo finished iscsiwatchdog >>/root/tmp2

 echo deleted knowns and added leader >>/root/tmp2
else
 echo found other host as primary.>>/root/tmp2
  leaderall=` ./etcdget.py leader --prefix `
  leader=`echo $leaderall | awk -F'/' '{print $2}' | awk -F"'" '{print $1}'`
  leaderip=`echo $leaderall | awk -F"')" '{print $1}' | awk -F", '" '{print $2}'`
   /TopStor/logmsg.py Partst04 info system $myhost $myip
  ./clearnamespace.py $enpdev
  ./cleardataip.py $enpdev
  if [ $knownsearch -eq 0 ];
  then
   echo starting etcd as local >>/root/tmp2
    ./etccluster.py 'local' $myip 2>/dev/null
   chmod +r /etc/etcd/etcd.conf.yml 2>/dev/null
   #rm -rf /var/lib/etcd/*
   systemctl daemon-reload 2>/dev/null
   systemctl stop etcd 2>/dev/null
   sleep 2
   systemctl start etcd 2>/dev/null
   while true;
   do
    echo starting etcd=$?
    systemctl status etcd
    if [ $? -eq 0 ];
    then
     break
    else
     systemctl start etcd
     sleep 1
    fi
   done
  fi
  /pace/etcdcmdlocal.py $myip user add root:YN-Password_123  2>/dev/null
  /pace/etcdcmdlocal.py $myip auth enable 2>/dev/null
  ./etcdputlocal.py $myip 'local/'$myhost $myip
  leaderip=` ./etcdget.py leader/$leader `
  /sbin/rabbitmqctl add_user rabb_$leader YousefNadody 2>/dev/null
  /sbin/rabbitmqctl set_permissions -p / rabb_$leader ".*" ".*" ".*" 2>/dev/null
  ./etcdget.py Active --prefix | grep $myhost
  if [ $? -ne 0 ];
  then
   ./etcdput.py possible$myhost $myip
   sleep 3
   stillpossible=1
   while [ $stillpossible==1 ]:
   do
    ./etcdget.py possible --prefix | grep $myhost
    if [ $? -eq 0 ];
    then
     stillpossible=1
    else
     stillpossible=0
    fi
   done 
  fi 
  stamp=`date +%s%N`
  myalias=`ETCDCTL_API=3 /pace/etcdgetlocal.py $myip $aliast/$myhost`
  ./etcddellocal.py $myip leader --prefix 
  ./etcdputlocal.py $myip leader/$leader $leaderip 
  ./etcddel.py sync/pools request/$myhost 2>/dev/null
  ./etcddellocal.py $myip pools --prefix 2>/dev/null
  ./etcddellocal.py $myip volumes --prefix 2>/dev/null
  ./etcddellocal.py $myip sync/pools Add_ 2>/dev/null
  ./etcddellocal.py $myip sync/pools Del_ 2>/dev/null
  ./etcddellocal.py $myip sync/volumes volumes_$stamp 2>/dev/null
  ./etcdput.py $aliast/$myhost $myalias
  myalias=`echo $myalias | sed 's/\_/\:\:\:/g'`
  myalias=`echo $myalias | sed 's/\//\:\:\:/g'`
  ./etcdput.py sync/$aliast/Add_${myhost}_$myalias/request ${aliast}_$stamp.
  ./etcdput.py sync/$aliast/Add_${myhost}_$myalias/request/$myhost ${aliast}_$stamp.
  issync=`./etcdgetlocal.py $myip sync initial`initial
  echo $issync | grep $myhost
  if [ $? -eq 0 ];
  then
   echo syncrequests only 
  ./checksyncs.py syncrequest
  else
   echo have to syncall
  ./checksyncs.py syncall $myip
  fi 

  echo requesting syncrequest
  /bin/crontab /TopStor/plaincron
  /TopStor/etctocron.py
  systemctl start iscsid &
  systemctl start iscsi &
  systemctl start topstorremote
  systemctl start topstorremoteack
  systemctl start servicewatchdog 
  echo etcd started as local >>/root/tmp2
  rm -rf /var/lib/iscsi/nodes/* 2>/dev/null
  echo starting iscsiwaatchdog >>/root/tmp2
  /sbin/zpool export -a
  /pace/iscsiwatchdog.sh $myip $myhost $leader 2>/dev/null
  echo started iscsiwaatchdog >>/root/tmp2
  echo /TopStor/syncq.py $leaderip $myhost >>/root/tmp2
  /TopStor/syncq.py $leaderip $myhost 2>/root/syncqerror
fi
/TopStor/HostgetIPs &
echo starting disk LIO check >>/root/tmp2
myhost=`hostname -s`
hostnam=`cat /TopStordata/hostname`
poollist='/pacedata/pools/'${myhost}'poollist';
lastreboot=`uptime -s`
seclastreboot=`date --date="$lastreboot" +%s`
secrunning=`cat $runningpools | grep runningpools | awk '{print $2}'`
if [ -z $secrunning ]; then
 echo hithere: $lastreboot : $seclastreboot
 secdiff=222;
else
 secdiff=$((seclastreboot-secrunning));
fi
if [ $secdiff -ne 0 ]; then
 echo runningpools $seclastreboot > $runningpools
echo starting keysend >>/root/tmp2
 ./keysend.sh $myip &>/dev/null
# pcs resource create IPinit ocf:heartbeat:IPaddr2 nic="$ccnic" ip="10.11.11.254" cidr_netmask=24 op monitor on-fail=restart 2>/dev/null
# pcs resource debug-start IPinit 2>/dev/null
 rm -rf /TopStor/key/adminfixed.gpg && cp /TopStor/factory/factoryadmin /TopStor/key/adminfixed.gpg
echo i all zpool exported >>/root/tmp2
 echo $freshcluster | grep 1
 if [ $? -eq 0 ];
 then 
#  sh iscsirefresh.sh
#  sh listingtargets.sh
  echo freshcluster=$freshcluster so zpool importing >>/root/tmp2
  #zpool import -a 2>/dev/null
   ./putzpool.py 2>/dev/null
  echo ran putzpool >>/root/tmp2
 fi
 touch /var/www/html/des20/Data/Getstatspid
fi
#zpool export -a
rm -rf /pacedata/forzfsping 2>/dev/null
ionice -c2 -n0 -p `pgrep etcd`
/TopStor/ioperf.py performance
echo fisniehd startzfs >>/root/tmp2

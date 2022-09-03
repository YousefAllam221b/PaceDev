#!/bin/sh
dmesg -n 1
if [[ "$#" -eq 0 ]];
then
 islocal=0
else
 islocal=1
 myip=`echo $@ | awk '{print $1}'`
 myhost=`echo $@ | awk '{print $2}'`
 leader=`echo $@ | awk '{print $3}'`
fi
pgrep iscsid -a
while [ $? -ne 0 ];
do
 sleep 1
 pgrep iscsid -a
done

pgrep etcd -a
while [ $? -ne 0 ];
do
 sleep 1
 pgrep etcd -a
done
echo start >> /root/iscsiwatch
sh /pace/iscsirefresh.sh
echo finished start of iscsirefresh  > /root/iscsiwatch
sh /pace/listingtargets.sh
   
echo finished listingtargets >> /root/iscsiwatch
echo updating iscsitargets >> /root/iscsiwatch
sh /pace/addtargetdisks.sh
echo finished updtating iscsitargets >> /root/iscsiwatch
if [[ $islocal -eq 0 ]];
then
 echo putzpool to leader >> /root/zfspingtmp
 echo putzpool to leader hi="$#" >> /root/iscsiwatch
 ETCDCTL_API=3 /pace/putzpool.py isciwatchversion &
 echo finished putzpool to leader hi="$#" >> /root/iscsiwatch
else
 echo putzpool local $myip $myhost $islocal >> /root/zfspingtmp
 echo putzpool local $myip $myhost $islocal >> /root/iscsiwatch
fi

pgrep checkfrstnode -a
if [ $? -ne 0 ];
then
 /pace/frstnodecheck.py
fi
/usr/bin/chronyc -a makestep
rebootstatus='thestatus'`cat /TopStordata/rebootstatus`
echo $rebootstatus | grep finish
if [ $? -ne 0 ];
then
 /TopStor/rebootme `cat /TopStordata/rebootstatus`  2>/root/rebooterr
fi

#!/bin/sh
lsscsi=`lsscsi -is | wc -c `
dmesg -n 1
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
sh /pace/disklost.sh
sh /pace/addtargetdisks.sh
ETCDCTL_API=3 /pace/putzpool.py 
lsscsi2=`lsscsi -is | wc -c `

echo $lsscsi | grep $lsscsi2
if [ $lsscsi -eq $lsscsi2 ];
then 
 echo '###############################################'
 /pace/zpooltoimport.py
 /pace/selectspare.py
 /pace/selectspare.py
 /pace/selectspare.py
 ./VolumeCheck.py
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

#!/bin/sh
export ETCDCTL_API=3
export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
myhost=`hostname -s `
thehost=`echo $@ | awk '{print $1}'`
myip=`echo $@ | awk '{print $2}'`
thehostip=`echo $@ | awk '{print $3}'`
./etcddellocal.py $myip pool $thehost
./etcddellocal.py $myip vol $thehost
#declare -a disks=(`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`);
declare -a disks=`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`;
iscsiadm -m node -p $thehostip:3266 -u 
echo "${disks[@]}"
echo $@ > /root/losthostparam
echo "${disks[@]}" > /root/losthost
echo pdisks=` echo "${disks[@]}" | awk '{print $1}' | awk -F'/' '{print $NF}' `
echo pdisks="${pdisks[@]}" >> /root/losthost
echo  "${disks[@]}" | while read l;
do
   dis=`echo $l | awk '{print $1}'  | awk -F'/' '{print $3}'`
   echo 1 > /sys/block/$dis/device/delete 2>/dev/null
   echo echo 1 \> /sys/block/$dis/device/delete >> /root/hostlost
done
echo udpating database >> /root/hostlosttmp
#ETCDCTL_API=3 /pace/etcdget.py pools --prefix | grep "\/$thehost" | grep "\/${myhost}" > /TopStordata/forlocalpools
ETCDCTL_API=3 /pace/etcddellocal.py $myip known/$thehost  --prefix
ETCDCTL_API=3 /pace/importnxtlocalpools.py $myip $myhost $thehost 
ETCDCTL_API=3 /pace/etcddellocal.py $myip hosts/$thehost  --prefix
ETCDCTL_API=3 /pace/etcddellocal.py $myip prop/$thehost

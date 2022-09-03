#!/bin/sh
cd /pace
export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
myhost=`hostname -s `
thehost=`echo $@ | awk '{print $1}'`
./etcdget.py sync/losthost --prefix | grep $thehost
issync=$?
echo issync=$issync ============================
if [ $issync -eq 0 ];
then
 local='local'
 myip=`/sbin/pcs resource show CC | grep Attrib | awk -F'ip=' '{print $2}' | awk '{print $1}'`
else
 local=''
 myip=''
fi
echo $local and $myip
exit
#declare -a disks=(`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`);
./etcddel${local}.py $myip pool $thehost
./etcddel${local}.py $myip vol $thehost
./etcdput${local}.py $myip tosync yes 
declare -a disks=`lsscsi -i | grep $thehost | awk '{print $6" "$7}'`;
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
echo disks="${disks[@]}" >> /root/hostlosttmp
echo "${disks[@]}" | awk '{print $2}'  | while read l;
do
 echo checking disk $l >> /root/hostlosttmp
 ETCDCTL_API=3 /pace/changeop.py $myhost scsi-$l 
done
echo udpating database >> /root/hostlosttmp
#ETCDCTL_API=3 /pace/etcdget.py pools --prefix | grep "\/$thehost" | grep "\/${myhost}" > /TopStordata/forlocalpools
ETCDCTL_API=3 /pace/etcddel${local}.py $myip known/$thehost  --prefix
ETCDCTL_API=3 /pace/etcddel${local}.py $myip ipaddr $thehost 
ETCDCTL_API=3 /pace/etcddel${local}.py $myip ready $thehost 
ETCDCTL_API=3 /pace/importlocalpools.py $myhost $thehost 
ETCDCTL_API=3 /pace/etcddel${local}.py $myip hosts/$thehost  --prefix
ETCDCTL_API=3 /pace/etcddel${local}.py $myip prop/$thehost
ETCDCTL_API=3 /pace/etcdput${local}.py $myip losthost/$thehost `date +%s` 
ETCDCTL_API=3 /pace/etcddel${local}.py $myip cannot  --prefix
ETCDCTL_API=3 /pace/etcddel${local}.py $myip oldhosts/$thehost  --prefix
ETCDCTL_API=3 /pace/putzpool.py 
if [ $issync -ne 0 ];
then
 stamp=`date +%s`
 /pace/etcddel.py sync/known _${thehost}
 /pace/etcdput.py sync/known/Del_${thehost}_--prefix/request known_$stamp
 /pace/etcdput.py sync/known/Del_${thehost}_--prefix/request/$myhost known_$stamp
 /pace/etcddel.py sync/ready _${thehost}
 /pace/etcdput.py sync/ready/Del_${thehost}_--prefix/request ready_$stamp
 /pace/etcdput.py sync/ready/Del_${thehost}_--prefix/request/$myhost ready_$stamp
 /pace/etcdput.py sync/losthost/hostlost.sh_${thehost}_--prefix/request losthost_$stamp
 /pace/etcdput.py sync/losthost/hostlost.sh_${thehost}_--prefix/request/$myhost losthost_$stamp
 /pace/etcddel.py sync/volumes _${thehost}
 /pace/etcdput.py sync/volumes/Del_${thehost}_--prefix/request/$myhost volumes_$stamp
 /pace/etcdput.py sync/volumes/Del_${thehost}_--prefix/request volumes_$stamp
 /pace/etcddel.py sync/pools _${thehost}
 /pace/etcdput.py sync/pools/Del_${thehost}_--prefix/request/$myhost pools_$stamp
 /pace/etcdput.py sync/pools/Del_${thehost}_--prefix/request pools_$stamp
 /pace/etcddel.py sync/poolsnxt _${thehost}
 /pace/etcdput.py sync/poolsnxt/Del_${thehost}_--prefix/request/$myhost poolsnxt_$stamp
 /pace/etcdput.py sync/poolsnxt/Del_${thehost}_--prefix/request poolsnxt_$stamp
fi
echo  it is done >> /root/hostlosttmp


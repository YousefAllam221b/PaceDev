#!/bin/sh
######################
#exit
##########################
cd /pace
myhost=`hostname -s`;
change=0
#declare -a iscsitargets=(`cat /pacedata/iscsitargets | awk '{print $2}' `);
declare -a iscsitargets=(`ETCDCTL_API=3 ./iscsiclients.py | grep target | awk -F'/' '{print $2}'`);
currentdisks=`targetcli ls /iscsi`
disks=(`lsblk -nS -o name,serial,vendor | grep -v sr0 | grep -vw sda | grep -v LIO | awk '{print $1}'`)
diskids=`lsblk -nS -o name,serial,vendor | grep -v sr0 | grep -vw sda | grep -v LIO | awk '{print $1" "$2}'`
mappedhosts=`targetcli ls /iscsi | grep Mapped`;
targets=`targetcli ls backstores/block | grep -v deactivated |  grep dev | awk -F'[' '{print $2}' | awk '{print $1}'`
tpgs=(`targetcli ls /iscsi | grep iqn | grep TPG | grep ':t1' | awk -F'iqn' '{print $2}' | awk '{print $1}'`)
myip=`/sbin/pcs resource show CC | grep Attributes | awk -F'ip=' '{print $2}' | awk '{print $1}'`
declare -a newdisks=();
targetcli ls iscsi/ | grep ".$myhost:t1" &>/dev/null
if [ $? -ne 0 ]; then
 targetcli iscsi/ create iqn.2016-03.com.${myhost}:t1 &>/dev/null
 targetcli iscsi/iqn.2016-03.com.$myhost:t1/tpg1/portals delete 0.0.0.0 3260
 targetcli iscsi/iqn.2016-03.com.$myhost:t1/tpg1/portals create $myip 3266
 change=1
fi
i=0;
echo diskids="${diskids[@]}"
for ddisk in "${disks[@]}"; do
 devdisk=`echo $ddisk | awk '{print $1}'`
 idisk=`echo "$diskids" | grep $ddisk | awk '{print $2}'`
 echo devid = $devdisk $idisk
done
for ddisk in "${disks[@]}"; do
 devdisk=$ddisk 
 echo ddisk===$ddisk
 idisk=`echo "$diskids" | grep -w $ddisk | awk '{print $2}'`
 echo devdisk-ddisk=$ddisk $idisk

 echo $currentdisks | grep $idisk &>/dev/null
 if [ $? -ne 0 ]; then
  echo Imhere
  pdisk=`ls /dev/disk/by-id/ | grep $idisk | grep -v part`
  targetcli backstores/block create ${devdisk}-${myhost} /dev/disk/by-id/$pdisk
  change=1
  echo currentdisks $currentdisks
  for iqn in "${tpgs[@]}"; do
   echo iqn= $iqn devdisk=$devdisk-${myhost}
   targetcli iscsi/iqn${iqn}/tpg1/luns/ create /backstores/block/${devdisk}-${myhost}  
   change=1
  done
 fi
done;
for target in "${iscsitargets[@]}"; do
 echo $mappedhosts | grep $target &>/dev/null
 if [ $? -ne 0 ]; then
   myip=`/pace/etcdget.py ActivePartners/$myhost`
  targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1/acls/ create iqn.1994-05.com.redhat:$target
  
  #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1 demo_mode_write_protect=0 
  #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1 generate_node_acls=1 
  #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1 set attribute authentication=1
  #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1 set auth userid=MoatazNegm 
  #targetcli iscsi/iqn.2016-03.com.${myhost}:t1/tpg1 set auth password=YNPassword121 

  change=1
 fi
done
targetcli saveconfig
if [ $change -eq 1 ];
then
 targetcli saveconfig /pacedata/targetconfig
 sleep 1 
fi

#!/bin/sh
result='nothing'
n=1
ipbase=''
for x in $( echo $1 | sed 's/\./ /g')
do
 n=$((n+1))
 if [ $n -gt 4 ]
 then
  break
 fi
 ipbase=${ipbase}$x'.' 
done
for x in {3..254}
do
 ip=${ipbase}$x
 checking=`nmap --max-rtt-timeout 20ms -p 2379 $ip | grep -v filtered `
 echo $checking | grep 'etcd-client' >/dev/null
 if [ $? -eq 0 ];
 then
  ETCDCTL_API=3 /bin/etcdctl --user=root:YN-Password_123 --endpoints=http://$ip:2379 get leader --prefix
  if [ $? -eq 0 ];
  then
   result=$ipbase`echo $checking | awk -F"$ipbase" '{print $2}' | awk -F')' '{print $1}'`
   /pace/runningetcdnodes.py $ip 2>/dev/null
   break
  fi
 fi
done
echo $result | awk '{print $1}'

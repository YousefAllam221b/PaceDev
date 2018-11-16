#!/bin/sh
rm -rf /pacedata/nodesearch.txt
touch /pacedata/forzfsping
/sbin/pcs property set stonith-enabled=false
nic=`/sbin/pcs resource show CC | grep nic | awk -F'nic=' '{print $2}' | awk '{print $1}'`
while [ $? -ne 0 ];
do
sleep 1;
nic=`/sbin/pcs resource show CC | grep nic | awk -F'nic=' '{print $2}' | awk '{print $1}'`
done
/sbin/pcs resource create IPinit ocf:heartbeat:IPaddr2 nic=$nic ip="10.11.11.254" cidr_netmask=24 op monitor on-fail=restart 2>/root/tmpinit
/sbin/pcs resource restart keyweb
while [ $? -ne 0 ];
do
sleep 1;
/sbin/pcs resource restart keyweb
done
rm -rf /pacedata/forzfsping
rm -rf /pacedata/forstartzfs
sleep 120
/sbin/pcs resource delete --force IPinit
/sbin/ip addr del 10.11.11.254/24 dev enp0s8 
/TopStor/factory.sh


#!/bin/sh
export PATH=/bin:/usr/bin:/sbin:/usr/sbin:/root
myhost=`hostname -s`
myaddCC=`echo $@ | awk '{print $1}'`
echo 127.0.0.1 localhost > /etc/hosts
echo $myaddCC $myhost >> /etc/hosts
echo 127.0.0.1 $myhost >> /etc/hosts

#!/bin/sh
echo $@ > /root/mkdm
dmname=${RANDOM}$RANDOM
dmsetup create $dmname  --table '0 195312500000000 zero'
 
dmsuff=`ls -lisah /dev/disk/by-id/dm-name-$dmname | awk -F'/' '{print $NF}'`
#./etcdput.py dm/$host/$dmname dm$dmsuff
#./broadcasttolocal.py dm/$host/$dmname dm$dmsuff
echo $dmsuff

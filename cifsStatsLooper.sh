#!/usr/bin/sh
cifsStats () {
	cd /TopStor
	/TopStor/containersStats.py $1
}
while true;
do
 cifsStats $1
 sleep 3
done

#!/usr/bin/sh
fapipy() {
cd /TopStor
/TopStor/fapi.py 1>/root/fapi.log 2>/root/fapierr.log 
}
while true;
do
 fapipy
 sleep 2 
done


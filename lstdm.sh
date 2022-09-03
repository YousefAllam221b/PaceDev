#!/bin/sh
ls -lisah /dev/disk/by-id/dm-name-* | awk -F'/' '{print $NF}'

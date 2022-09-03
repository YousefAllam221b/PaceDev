#!/usr/bin/sh
iscsiwatchdogsh () {
cd /pace
/pace/iscsiwatchdog.sh 
}
pkill isciswatchdoglooper.sh
while true;
do
 iscsiwatchdogsh
 sleep 10 
done


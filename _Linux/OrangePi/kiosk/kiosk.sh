#!/bin/bash

sleep 10
 
xset s noblank
xset s off
xset -dpms
 
unclutter -idle 0.5 -root &
 
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' /home/orangepi/.config/chromium/Default/Preferences
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' /home/orangepi/.config/chromium/Default/Preferences
 
/usr/bin/chromium --noerrdialogs --disable-infobars --kiosk http://localhost:8000
 

#!/bin/sh
# startup.sh
# runs the sonatome_teller.py script, meant to be executed upon startup of the rpi

cd /
cd /home/pi/git/ctd-design-studio/src/pi
sudo python3 sonatome_teller.py
cd /
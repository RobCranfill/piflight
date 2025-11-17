#!/bin/bash
# script to run piflight at startup

cd /home/rob/proj/piflight/piflight
./start_dump1090.sh

. env/bin/activate
python3 piflight


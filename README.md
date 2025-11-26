# piflight
A simple app that shows aircraft in the sky around me,
using a cheap USB Software Defined Radio (SDR)
and a Rasperry Pi Zero.


## Requirements
* Hardware
  * Raspberry Pi Zero 2W
    * We don't use WiFi for this project (but it makes development so much easier!), so a non-WiFi RP Zero might work - but that might not have enough processing power for this, I haven't tried.
  * Adafruit 1.3" TFT display
  * USB SDR dongle - I use https://www.nooelec.com/store/qs
* Software
  * Python 3.13 or so (3.13.5 used)
  * Adafruit 'Blinka' libraries
  * Python Imaging Library
  * py1090 (standard lib via pip3)

## Installation
  * 

## Installation of startup service
To make the PiZero automatically run PiFlight at startup.

### Service file
* Edit piflight_startup.service so that the path for the 'cd' is correct, then do the following:
```
 sudo cp piflight_startup.service /lib/systemd/system/
 sudo chmod 644 /lib/systemd/system/piflight_startup.service
 sudo systemctl enable piflight_startup.service
```
### To stop the service
You can kill or pkill it, or send a SIGINT or SIGTERM (same thing).



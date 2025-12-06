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

## ConOps
You define (see below) your geographical area of interest (via a latitude/longitude bounding box)
and we display all aircraft with coodinates in that area. These blips are mapped to the LCD display,
which is just a static image you grabbed from Google Maps or whatever.

Since this project is displaying live over-the-air data received from the radio, your area of interest must be
the area actually surrounding you - you can't just pick some random area of the world (like you can
in, say, FlightRadar).


## Customization
To make this work for your location, you need to do two things: configure your latitude and longitude, 
and create a background image to display.

As described above, the code will use the area defined to map the locations of the aircraft onto the display.
As I live near a major international airport, I picked a box about 15 miles on a side, centered over my house -
your box might need to be bigger or smaller.

You need to create a file "background.png" file, which needs to be compatible with Pillow's Image.open() method.
I used an 8-bit sRGB PNG file, but other formats may work too. 


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



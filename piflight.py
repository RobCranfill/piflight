"""
My own FlightAware.
(c)2025 rob cranfill
 - for RPi Zero2W, using "Blinka" and dump1090-fa.

Things to do/fix:
    - when there are no messages, blinky thing doesn't blink.
    - color according to a/c alt? tried, doesn't work. :-/
"""

import time

# adafruit libs
from adafruit_rgb_display import st7789
import board
import digitalio
import keypad
from PIL import Image, ImageDraw, ImageFont

# 3rd party libs
import py1090

# our libs
import geo

SHOW_CALIBRATION_POINTS = False
CALIB_LOCS = [geo.lat_long(47.655935, -122.327958)]


BLINK_COLORS = [(255,0,0)] # just red is fine

# constanty-global things
BACKLIGHT_PIN = board.D22
WIDTH = 240
HEIGHT = 240
FONT_ARIAL20 = ImageFont.truetype(r'fonts/arial.ttf', 20) 

# Stop drawing a blip if we don't see it in this many seconds
AP_TIME_EXPIRE = 15 


class ap_info():
    """The a/c dump1090 record, and the last time we got data for this a/c."""

    def __init__(self, dump_msg, last_seen_time):
        """dump_msg is the entire dump1090 record."""
        self.dump_msg = dump_msg
        self.last_seen_time = last_seen_time

    def __str__(self):
        return f"{self.dump_msg.hexident}"


def setup_hardware():

    # Configuration for CS and DC pins (these are PiTFT defaults):
    cs_pin = digitalio.DigitalInOut(board.CE0)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = digitalio.DigitalInOut(board.D24)

    # Config for display baudrate (default max is 24mhz):
    BAUDRATE = 24000000

    # Setup SPI bus using hardware SPI:
    spi = board.SPI()

    # Create the display:
    disp = st7789.ST7789(
        spi,
        cs=cs_pin, dc=dc_pin, rst=reset_pin,
        baudrate=BAUDRATE,
        width=WIDTH, height=HEIGHT,
        x_offset=0, y_offset=80
    )

    # Turn on the backlight
    backlight = digitalio.DigitalInOut(BACKLIGHT_PIN)
    backlight.switch_to_output()
    backlight.value = True

    image = Image.new("RGB", (WIDTH, HEIGHT))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=(0, 0, 0))
    disp.image(image)

    return disp


def backlight_off():
    backlight = digitalio.DigitalInOut(BACKLIGHT_PIN)
    backlight.switch_to_output()
    backlight.value = False

def load_image(display, image_path):

    image = Image.open(image_path)
    print("Image loaded OK")

    # Scale the image to the smaller screen dimension
    image_ratio = image.width / image.height
    screen_ratio =  HEIGHT / WIDTH
    if screen_ratio < image_ratio:
        scaled_width = image.width * HEIGHT // image.height
        scaled_height = HEIGHT
    else:
        scaled_width = WIDTH
        scaled_height = image.height * WIDTH // image.width
    image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

    # Crop and center the image
    x = scaled_width // 2 - WIDTH // 2
    y = scaled_height // 2 - HEIGHT // 2
    image = image.crop((x, y, x + WIDTH, y + HEIGHT))

    # # Display the image
    # display.image(image)

    return image

# def show_blip(display_object, image_object, x, y, color_tuple):

#     temp_image = image_object.copy()
#     draw = ImageDraw.Draw(temp_image)
#     draw.rectangle((x, y, x+5, y+5), fill=color_tuple)
#     display_object.image(temp_image)


STATUS_Y = 220

def show_status(display_object, image_object, text):
    """This *does* modifiy the image_object."""

    draw = ImageDraw.Draw(image_object)

    # black-out area
    draw.rectangle((0, STATUS_Y, WIDTH, HEIGHT), fill=0)
    draw.text((5, STATUS_Y), text,
            fill=None, font=FONT_ARIAL20, anchor=None, spacing=0, align="left")    

# Low is black, high is blue, medium unused?
COLOR_LOW = (0, 0, 0)
COLOR_MED = (0, 255, 0)
COLOR_HIGH = (0, 0, 255)

# NOT WORKING :-/
# COLOR_LOW = (0,0,0)
# COLOR_MED = (0,0,0)
# COLOR_HIGH = (0,0,0)

def get_color_for_altitude(alt):

    if alt is None:
        return (0,0,0) # ? actually we are ignoring a/c with no alt

    if alt < 4000:
        return COLOR_LOW
    # if alt < 10000:
    #     return COLOR_MED
    return COLOR_HIGH


def show_airplanes(mapper, display, image, airplane_dict):
    """Also expire a/c dict; airplane_dict is dict of [str, ap_info]"""

    # We will draw on a copy of the base map image.
    new_image = image.copy()
    draw = ImageDraw.Draw(new_image)

    # can't modify a dict we are iterating,
    # so keep a list of ones to remove when we are done.
    #
    keys_to_delete = []
    visible_ac = 0
    for ap in airplane_dict.values():

        t_last = ap.last_seen_time
        if t_last < time.monotonic() - AP_TIME_EXPIRE:
            print(f"Expire {ap.dump_msg.hexident}")
            keys_to_delete.append(ap.dump_msg.hexident)
        else:
            ll = geo.lat_long(ap.dump_msg.latitude, ap.dump_msg.longitude)
            x, y = mapper.map_lat_long_to_x_y(ll)
            if x >= 0 and x <= WIDTH and y >= 0 and y <= STATUS_Y: # don't paint in the status area
                visible_ac += 1
                c = get_color_for_altitude(ap.dump_msg.altitude)
                # c = (0,0,0)
                # print(f"  {ap} @ {ap.dump_msg.altitude} -> {c} @ {x},{y}")
                draw.rectangle((x, y, x+5, y+5), fill=c)
            else:
                pass
                # print(f"  {ap} is offscreen at {ap.dump_msg.latitude}, {ap.dump_msg.longitude}")

    # show_status(display, image, f"{len(airplane_dict)-len(keys_to_delete)} aircraft")

    # Also show calibration points?
    if SHOW_CALIBRATION_POINTS:
        c = (0,0,255)
        for ll in CALIB_LOCS:
            x, y = mapper.map_lat_long_to_x_y(ll)
            if True or x >= 0 and x <= WIDTH and y >= 0 and y <= STATUS_Y: # don't paint in the status area
                print(f" CALIB_LOCS = {x},{y}")
                draw.rectangle((x-4, y-4, x+4, y+4), fill=c)
            else:
                print(f" CALIB_LOCS {ll} is offscreen at {ll.lat}, {ll.long}")

    # This draws onto the given image but doesn't display it yet.
    show_status(display, new_image, f"{visible_ac} aircraft")

    global last_blink
    if last_blink < int(time.monotonic()):
        color = BLINK_COLORS[last_blink % len(BLINK_COLORS)]
        draw.rectangle((WIDTH-15, STATUS_Y+5, WIDTH, STATUS_Y+20), fill=color)
        last_blink = int(time.monotonic())

    # display it
    display.image(new_image)

    # now delete expired planes from list
    for k in keys_to_delete:
        del airplane_dict[k]
    # print(f" =--> {list(airplane_dict.keys())}")


############### start of main code

display_obj = setup_hardware()
basemap_image = load_image(display_obj, "SEA-240x240.png")
display_obj.image(basemap_image)

# for if and when we use these:
keys = keypad.Keys((board.D23,board.D24), value_when_pressed=False, pull=True)

all_messages = 0
ok_messages = 0
in_area_messages = 0

last_blink = int(time.monotonic())

# set up geographical mapper
ul = geo.lat_long(47.715, -122.48)
lr = geo.lat_long(47.48, -122.138)
mapper  = geo.mapper(ul, lr, (240, 240))

# for debug
CALIB_LOCS.append(ul)
CALIB_LOCS.append(lr)

# Keep and paint this list of a/c.
airplanes = dict()


try:
    with py1090.Connection() as connection:

        print("dump1090 connection OK....")
        show_status(display_obj, basemap_image, "dump1090 connection OK....")
        time.sleep(2)

        for line in connection:
            # print(line)

            # Happens occasionally
            try:
                msg = py1090.Message.from_string(line)
            except IndexError:
                print("**** Error parsing message! Continuing....")
                continue

            if msg.message_type == 'MSG':
                all_messages += 1

                if not None in [msg.hexident, msg.latitude, msg.longitude]:
                    ok_messages += 1

                    # to see everthing, use this:
                    # print(f"  {msg.__dict__=}")

                    hi = msg.hexident
                    if airplanes.get(hi) is None:
                        print(f"New airplane {hi}")
                    airplanes[hi] = ap_info(msg, time.monotonic())
                    # print(f" {len(airplanes)} {airplanes=}")

            show_airplanes(mapper, display_obj, basemap_image, airplanes)

            event = keys.events.get()
            if event is None:
                # event will be None if nothing has happened. Do background stuff?
                pass
            else:
                print(event)
                # if event.key_number == 0:
                #     do_something()
                # if event.key_number == 1:
                #     do_something_else()

except ConnectionRefusedError:
    print("Can't connect! Is dump1090 running?")
except KeyboardInterrupt:
    print("\nOK, fine!")
    backlight_off()

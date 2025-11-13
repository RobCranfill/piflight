"""
My own FlightAware.
(c)2025 rob cranfill
 - for RPi Zero2W, using "Blinka" and dump1090-fa.

Things to do
    - status line

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


WIDTH = 240
HEIGHT = 240

FONT_ARIAL20 = ImageFont.truetype(r'fonts/arial.ttf', 20) 


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
    backlight = digitalio.DigitalInOut(board.D26)
    backlight.switch_to_output()
    backlight.value = True

    image = Image.new("RGB", (WIDTH, HEIGHT))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=(0, 0, 0))
    disp.image(image)

    return disp

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

def show_blip(display_object, image_object, x, y, color_tuple):

    temp_image = image_object.copy()
    draw = ImageDraw.Draw(temp_image)
    draw.rectangle((x, y, x+5, y+5), fill=color_tuple)
    display_object.image(temp_image)


STATUS_Y = 220

def show_status(display_object, image_object, text):
    """This *does* modifiy the origianal image."""

    draw = ImageDraw.Draw(image_object)

    # black-out area
    draw.rectangle((0, STATUS_Y, WIDTH, HEIGHT), fill=0)
    draw.text((5, STATUS_Y), text,
            fill=None, font=FONT_ARIAL20, anchor=None, spacing=0, align="left")    


AP_TIME_EXPIRE = 15 # seconds

def show_airplanes(display, image, airplane_dict):
    """Also expire a/c dict; dict of ap_info"""

    temp_image = image.copy()
    draw = ImageDraw.Draw(temp_image)

    hex_to_delete = []
    for ap in airplane_dict.values():

        t_last = ap.last_seen_time
        if t_last < time.monotonic() - AP_TIME_EXPIRE:
            print(f"Expire {ap.dump_msg.hexident}")
            hex_to_delete.append(ap.dump_msg.hexident)
        else:
            ll = geo.lat_long(ap.dump_msg.latitude, ap.dump_msg.longitude)
            x, y = m.map_lat_long_to_x_y(ll)
            if x >= 0 and x <= WIDTH and y >= 0 and y <= HEIGHT:
                draw.rectangle((x, y, x+5, y+5), fill=(0,0,0))

    show_status(display, image, f"{len(airplane_dict)-len(hex_to_delete)} aircraft")

    display.image(temp_image)

    # now delete from list
    for h in hex_to_delete:
        del airplane_dict[h]

    return len(airplane_dict)

class ap_info():
    """The a/p info, and the last time we got data for this a/p."""
    def __init__(self, dump_msg, last_seen_time):
        self.dump_msg = dump_msg
        self.last_seen_time = last_seen_time


############### start of main code

display_obj = setup_hardware()
map_image_obj = load_image(display_obj, "SEA-240x240.png")
display_obj.image(map_image_obj)

keys = keypad.Keys((board.D23,board.D24), value_when_pressed=False, pull=True)

x = 10
y = 10

color = (0)

all_messages = 0
ok_messages = 0
in_area_messages = 0

# set up geographical mapper
ul = geo.lat_long(47.7, -122.5)
lr = geo.lat_long(47.5, -122.0)
m  = geo.mapper(ul, lr, (200, 200))

# Keep and paint this list of a/c.
airplanes = dict()


try:
    with py1090.Connection() as connection:
        print("Connection OK....")
        time.sleep(2)
        show_status(display_obj, map_image_obj, "Connection OK....")

        for line in connection:
            # print(line)
            msg = py1090.Message.from_string(line)
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

                    n_aps = show_airplanes(display_obj, map_image_obj, airplanes)
                    # show_status(display_obj, map_image_obj, arial20, f"{n_aps} airplanes")

        event = keys.events.get
        if event is None:
            # event will be None if nothing has happened. Do background stuff?
            pass
        else:
            print(event)
            # if event.key_number == 0:
            #     x += 2
            # if event.key_number == 1:
            #     y += 2
            # show_blip(display_obj, map_image_obj, x, y, color)


except ConnectionRefusedError:
    print("Can't connect!")

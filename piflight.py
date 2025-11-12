"""
My own FlightAware.
(c)2025 rob cranfill
 - for RPi Zero2W, using "Blinka" and dump1090-fa.

Things to do
    - how to 'expire' an airplane?
    - status line

"""

import time

# adafruit libs
from adafruit_rgb_display import st7789
import board
import digitalio
import keypad
from PIL import Image, ImageDraw

# 3rd party libs
import py1090

# our libs
import geo


WIDTH = 240
HEIGHT = 240

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


def show_airplanes(display, image, airplane_dict):

    temp_image = image.copy()
    draw = ImageDraw.Draw(temp_image)

    for ap in airplane_dict.values():

        ll = geo.lat_long(ap.latitude, ap.longitude)
        x, y = m.map_lat_long_to_x_y(ll)
        print(f"  -> ({x}, {y})")

        if x >= 0 and x <= WIDTH and y >= 0 and y <= HEIGHT:
            draw.rectangle((x, y, x+5, y+5), fill=(0,0,0))

    display.image(temp_image)


############### start of code

display_obj = setup_hardware()
map_image_obj = load_image(display_obj, "SEA-240x240.png")
display_obj.image(map_image_obj)

keys = keypad.Keys((board.D23,board.D24), value_when_pressed=False, pull=True)

x = 10
y = 10

color = (0)

all_messages = 0
latlon_messages = 0
in_area_messages = 0

# set up geographical mapper
ul = geo.lat_long(47.7, -122.5)
lr = geo.lat_long(47.5, -122.0)
m  = geo.mapper(ul, lr, (200, 200))

airplanes = dict()

try:

    with py1090.Connection() as connection:
        print("Connection OK....")
        for line in connection:
            # print(line)
            msg = py1090.Message.from_string(line)
            if msg.message_type == 'MSG':
                all_messages += 1

                if not None in [msg.hexident, msg.latitude, msg.longitude]:

                # if msg.latitude is not None and msg.longitude is not None:

                    latlon_messages += 1

                    # to see everthing, use this:
                    # print(f"  {msg.__dict__=}")

                    # print(f"{msg.message_type=}")
                    # print(f"  {msg.callsign=}")
                    # print(f"  {msg.squawk=}")
                    # print(f"  {msg.altitude=}")
                    # print(f"  {msg.vertical_rate=}")
                    # print(f"  {msg.latitude=}")
                    # print(f"  {msg.longitude=}")
                    
                    # print(f"- {latlon_messages} of {all_messages}")

                    hi = msg.hexident
                    if airplanes.get(hi) is None:
                        print(f"New airplane {hi}")
                    airplanes[hi] = msg
                    # print(f" {len(airplanes)} {airplanes=}")

                    show_airplanes(display_obj, map_image_obj, airplanes)


        event = keys.events.get
        if event is None:
            # event will be None if nothing has happened. Do background stuff.
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

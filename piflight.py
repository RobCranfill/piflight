"""
My own FlightAware.
(c)2025 rob cranfill
 - for RPi Zero2W, using "Blinka" and dump1090-fa.  
"""

import board
import digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789
import time
import keypad

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
    temp_image = map_image_obj.copy()
    draw = ImageDraw.Draw(temp_image)
    draw.rectangle((x, y, x+5, y+5), fill=color_tuple)
    display_object.image(temp_image)


# keeping and re-using the draw object here didn't work. fine.
display_obj = setup_hardware()
map_image_obj = load_image(display_obj, "SEA-240x240.png")
display_obj.image(map_image_obj)


# while True:
#     for x in range(20, 200):
#         mess_with_image = map_image_obj.copy()
#         draw = ImageDraw.Draw(mess_with_image)
#         draw.rectangle((x, 100, x+5, 105), fill=(255, 0, 0))
#         display_obj.image(mess_with_image)
#         time.sleep(.05)


keys = keypad.Keys((board.D23,board.D24), value_when_pressed=False, pull=True)

x = 10
y = 10

color = (0)

while True:
    event = keys.events.get()
    if event is None:
        # event will be None if nothing has happened. Do background stuff.
        pass
    else:
        print(event)
        show_blip(display_obj, map_image_obj, x, y, color)
        x += 2


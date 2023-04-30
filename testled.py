
from time import sleep
from neopixel import Neopixel

number_leds = 9
led_strip = Neopixel(number_leds, 0, 28, "GRB")

def set_arms(num):
    global led_strip
    global number_leds
    white = (120, 120, 120)
    black = (0, 0, 0)
    
    for led in range(0, (number_leds-1)):
        if led < num:
            led_strip.set_pixel(led, white)
        else:
            led_strip.set_pixel(led, black)
    led_strip.show()
            
for num in range(0, number_leds+1):
    set_arms(num)
    sleep(1)
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
import jpegdec
from time import sleep
from pimoroni import RGBLED, Button
import gc
from gui import Listbox, ChooseItem

gc.collect()

display = PicoGraphics(DISPLAY_PICO_DISPLAY_2, rotate=270)
WIDTH, HEIGHT = display.get_bounds()

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

blackpen = display.create_pen(0,0,0)

display.set_pen(blackpen)
display.set_clip(0,0,WIDTH,HEIGHT)
display.clear()
display.remove_clip()

print(f'Display: Height={HEIGHT} Width={WIDTH}')

data = ['Apple', 'Pear', 'Giraffe', 'Polo','t1','t2','t3','t4','t5','t6','t7','t8','t9','t10','t11','t12','t13']
while True or KeyboardInterrupt:
    selected, value = ChooseItem(display, data, 1)
    if (selected):
        print(f'Selected: {data[value]}')
    else:
        print(f'Cancelled: {data[value]}')
#inset = 0
#top = 30
#left = 0
#right = 0
#bottom = 30
#labels(display=display, width=WIDTH, height=HEIGHT, b='Cancel', a='Save', y='Up', x='Down')
#box = Listbox(display=display, items=data, x=left, y=inset+top, width=WIDTH-(left+right), height=HEIGHT-(top+bottom))
#
#box.draw()
#while True or KeyboardInterrupt:
#    if button_x.read():
#        box.down()
#    if button_y.read():
#        box.up()

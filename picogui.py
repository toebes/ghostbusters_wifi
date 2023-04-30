from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
import jpegdec
from pimoroni import RGBLED, Button
import gc
import math

# 
class PicoGUI():
    def __init__(self, item_height = 20, label_height=20):
        self.item_height = item_height
        self.label_height = label_height

        self.display = PicoGraphics(DISPLAY_PICO_DISPLAY_2, rotate=270)

        self.display_width, self.display_height = self.display.get_bounds()
        self.whitepen = self.display.create_pen(255,255,255)
        self.blackpen = self.display.create_pen(0,0,0)
        self.highlightpen = self.display.create_pen(255,0,0)
        self.orangepen = self.display.create_pen(255,165,0)
        self.greenpen = self.display.create_pen(0,128,0)
        self.redpen = self.display.create_pen(200,0,0)
        self.yellowpen = self.display.create_pen(255,255,0)
        
        self.button_a = Button(12, repeat_time=500)
        self.button_b = Button(13, repeat_time=500)
        self.button_x = Button(14, repeat_time=500)
        self.button_y = Button(15, repeat_time=500)

    def rect(self, x, y, width, height, pen=None):
        """
        Sets a rectangle of the screen to fixed color
        
        Arguments:
        x      -  Left index (0 based) of rectangle
        y      -  Top index (0 based) of rectangle
        width  - number of pixels wide of rectangle
        height - number of pixels tall of rectangle
        pen    - Color pen to fill with (defaults to black)
        """
        if pen is None:
            pen = self.blackpen
        self.display.set_pen(pen)
        self.display.set_clip(x,y,width,height)
        self.display.clear()
        self.display.remove_clip()
        
    def clear(self):
        """
        Clears the entire screen to black
        """
        self.rect(0, 0, self.display_width, self.display_height, self.blackpen)
        
    def text(self, text, x, y, pen = None):
        """
        Displays text in a pen at a location
        """
        if pen is not None:
            self.display.set_pen(pen)
        self.display.text(text, x, y)
        
    def centertext(self, x, y, text, width, height = None, textpen = None, clearpen = None):
        """
        Centers text in a rectangular area, truncating on the right if it is too wide for the area
        
        Arguments:
        x        - Left index (0 based) of area for text
        y        - Top index (0 based) of area for text
        text     - Text to display in the box
        width    - Width of box to display text in
        height   - Height of box to display text in
        textpen  - pen to render text with (default = black)
        clearpen - pen to render text box with (default = white)
        
        """
        if height is None:
            height = self.label_height
        if textpen is None:
            textpen = self.blackpen
        if clearpen is None:
            clearpen = self.whitepen
        self.display.set_clip(x,y,width,height)
        self.display.set_pen(clearpen)
        self.display.clear()
        self.display.set_pen(textpen)
        txtwidth=self.display.measure_text(text)
        left = int((width-txtwidth)/2)
        if left < 0:
            left = 0
        # Draw the text in the box one pixel down from the top
        self.display.text(text,x+left,y+1)
        self.display.remove_clip()

    def labels(self, b='Cancel', a='Save', y='Up', x='Down'):
        """
        Display labels for the buttons on the display
        
        Arugments:
        b      - Label for upper left corner (default = Cancel)
        a      - Label for upper right corner (default = Save)
        y      - Label for lower left corner (default = Up)
        x      - Label for lower right cornder (default = Down)
        """
        width = self.display_width
        height = self.display_height

        # Compute label width and positions
        label_width = int(2*width/5)
        axleft = width-label_width
        xytop = height-self.label_height

        self.centertext(x=0,      y=0,     width=label_width, text=b)
        self.centertext(x=axleft, y=0,     width=label_width, text=a)
        self.centertext(x=0,      y=xytop, width=label_width, text=y)
        self.centertext(x=axleft, y=xytop, width=label_width, text=x)

    def box(self,x,y,width,height, pen=None):
        """
        Draws a rectangular box outline
        
        Arguments:
        x        - Left index (0 based) of area for box
        y        - Top index (0 based) of area for box
        width    - Width of box
        height   - Height of box
        pen      - pen to render text with (default = black)
        """
        if pen is None:
            pen = self.blackpen
        self.display.set_pen(pen)
        self.display.line(x,       y,        x+width, y)
        self.display.line(x+width, y,        x+width, y+height)
        self.display.line(x+width, y+height, x,       y+height)
        self.display.line(x,       y+height, x,       y)
        
    def update(self):
        self.display.update()
        
    def draw_jpg(self, filename,x = 0, y = 0, width=None, height = None):
        if width is None:
            width = self.display_width
        if height is None:
            height = self.display_height
            
        j = jpegdec.JPEG(self.display)

        # Open the JPEG file
        j.open_file(filename)

        self.display.set_clip(x, y, width, height)

        # Decode the JPEG
        j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)
        self.display.remove_clip()
        self.display.update()

def defaultrender(picogui, item, x, y):
    picogui.display.text(item, x, y)

class Listbox():
    """
    Create a list box for selecting data
    
    Arguments:
    picogui - Instantiated PicoGui class
    items   - Array of items to render
    x       - coordinate (0 based) of left side of box
    y       - coordinate (0 based) of top side of box
    width   - Width in pixels of the box
    height  - Height in pixels of the box
    render  - Optional render routine
    """
    selected = 0
    item_height = 20
    topitem = 0
    textoffset = 2
    
    def __init__(self, picogui, items, x, y, width, height, renderfunc = None):
        self.picogui = picogui
        self.data = items
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        if renderfunc is None:
            self.renderfunc = defaultrender
        else:
            self.renderfunc = renderfunc
    
    def __post_init__(self):
        self.draw()
    
    def draw(self):
        display = self.picogui.display
        # Clear area
        display.set_pen(self.picogui.whitepen)
        display.set_clip(self.x, self.y,self.width, self.height)
        display.clear()
        # Draw items
        no_of_items = len(self.data)
        # Figure out how many will show on the screen and make sure that the selected item
        # is in range of the items.
        screen_items = math.floor(self.height / self.item_height)
           
        if self.selected < self.topitem:
           self.topitem = self.selected
        if self.selected >= (self.topitem + screen_items):
           self.topitem = self.selected-(screen_items-1)

        if screen_items >= no_of_items:
            screen_items = no_of_items
            self.topitem = 0
        #print(f'Selected={self.selected} Top={self.topitem} Screen_items={screen_items} no_of_items={no_of_items}')

        for line in range(0, screen_items):
            offy = self.y +(line*self.item_height)
            entry = line+self.topitem
            #print(f'Line {line} X:{self.x} Y:{offy} Text:{self.data[entry]}')
            if entry == self.selected:
                display.set_pen(self.picogui.highlightpen)
                display.rectangle(self.x, offy, self.width, self.item_height)
                display.set_pen(self.picogui.whitepen)
            else:
                display.set_pen(self.picogui.whitepen)
                display.rectangle(self.x, offy, self.width, self.item_height)
                display.set_pen(self.picogui.highlightpen)
            self.renderfunc(picogui = self.picogui, item=self.data[entry], x=self.x + self.textoffset, y=offy)
        display.remove_clip()
        display.update()
        
    def select(self, item):
        self.selected = item

    def down(self):
        if self.selected == len(self.data)-1:
            self.draw()
            return
        if self.selected < len(self.data)-1:
            self.selected += 1
        self.draw()
        #print(f'down button pressed, selected item = {self.selected}')

    def up(self):
        if self.selected == 0:
            self.draw()
            return
    
        if self.selected > 0:
            self.selected -= 1 
        self.draw()
        #print(f'up button pressed, selected item = {self.selected}')

def ChooseItem(picogui, data, initial=0, renderfunc = None):
    inset = 0
    top = 30
    left = 0
    right = 0
    bottom = 30
    picogui.labels()
    box = Listbox(picogui, items=data, x=left, y=inset+top, width=picogui.display_width-(left+right), height=picogui.display_height-(top+bottom), renderfunc=renderfunc)
    if (box.selected != initial):
        box.select(initial)

    box.draw()
    while True or KeyboardInterrupt:
        if picogui.button_x.read():
            box.down()
        if picogui.button_y.read():
            box.up()
        if picogui.button_b.read():
            return (False, initial)
        if picogui.button_a.read():
            return (True, box.selected)

def ChooseVal(picogui, title, initial=0, limit_low = 0, limit_high = 0, callback=None):
    inset = 0
    left = 10
    right = 10
    height = picogui.item_height*5
    value = initial
    width = picogui.display_width-(left+right)
    top = int((picogui.display_height-height)/2)
    titletop = top + picogui.item_height
    valuetop = top + picogui.item_height*3
    picogui.clear()
    picogui.labels()
    picogui.rect(x=left, y=top, width=width, height=height, pen=picogui.whitepen)
    picogui.centertext(x=left, y=titletop, text=title, width=width)
    picogui.centertext(x=left, y=valuetop, text=str(initial), width=width)
    picogui.update()

    while True or KeyboardInterrupt:
        if picogui.button_x.read():
            if value > limit_low:
                value = value-1
                picogui.centertext(x=left, y=valuetop, text=str(value), width=width)
                if callback is not None:
                    callback(picogui, value)
                picogui.update()

        if picogui.button_y.read():
            if value < limit_high:
                value = value+1
                picogui.centertext(x=left, y=valuetop, text=str(value), width=width)
                if callback is not None:
                    callback(picogui, value)
                picogui.update()

        if picogui.button_b.read():
            return (False, initial)
        if picogui.button_a.read():
            return (True, value)

def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q
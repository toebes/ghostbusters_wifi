import math

class Listbox():
    highlight = {
        'red': 255,
        'green':0,
        'blue':0,}
    
    default = {
        'red': 255,
        'green':255,
        'blue':255,}
    
    selected = 0
    item_height = 20
    topitem = 0
    textoffset = 2
    
    def __init__(self, display, items, x, y, width, height):
        self.data = items
        self.display = display
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        print(f'len of data: {len(self.data)}')
    
    def __post_init__(self):
        self.draw()
    
    def draw(self):
        # Clear area
        white = self.display.create_pen(255,255,255)
        self.display.set_pen(white)
        self.display.set_clip(self.x, self.y,self.width, self.height)
        self.display.clear()
        # Draw border
        
        # Draw items
        
        # setup pens
        highlight = self.display.create_pen(self.highlight['red'],self.highlight['green'], self.highlight['blue'])
        default = self.display.create_pen(self.default['red'],self.default['green'], self.default['blue'])
        no_of_items = len(self.data)
        # Figure out how many will show on the screen and make sure that the selected item
        # is in range of the items.
        screen_items = math.floor(self.height / self.item_height)
        if self.selected < self.topitem:
           self.topitem = self.selected
        if self.selected >= (self.topitem + screen_items):
           self.topitem = self.selected-(screen_items-1)
        #print(f'Selected={self.selected} Top={self.topitem} Screen_items={screen_items}')
        
        for line in range(0, screen_items):
            offy = self.y +(line*self.item_height)
            entry = line+self.topitem
            #print(f'Line {line} X:{self.x} Y:{offy} Text:{self.data[entry]}')
            if entry == self.selected:
                self.display.set_pen(highlight)
                self.display.rectangle(self.x, offy, self.width, self.item_height)
                self.display.set_pen(default)
            else:
                self.display.set_pen(default)
                self.display.rectangle(self.x, offy, self.width, self.item_height)
                self.display.set_pen(highlight)
                
            self.display.text(self.data[entry], self.x + self.textoffset, offy)
        self.display.remove_clip()
        self.display.update()
        
    def select(self, item):
        self.selected = item

    def down(self):
        if self.selected == len(self.data)-1:
            self.draw()
            return
        if self.selected < len(self.data)-1:
            self.selected += 1
        self.draw()
        print(f'down button pressed, selected item = {self.selected}')

    def up(self):
        if self.selected == 0:
            self.draw()
            return
    
        if self.selected > 0:
            self.selected -= 1 
        self.draw()
        print(f'up button pressed, selected item = {self.selected}')

def centerbox(display,x,y,width,height,text,textpen,clearpen):
    display.set_clip(x,y,width,height)
    display.set_pen(clearpen)
    display.clear()
    display.set_pen(textpen)
    txtwidth=display.measure_text(text)
    left = int((width-txtwidth)/2)
    if left < 0:
        left = 0
    display.text(text,x+left,y+1)
    display.remove_clip
    

def labels(display, width, height, b, a, y, x):
    label_height = 20
    label_width = int(2*width/5)
    axleft = width-label_width
    xytop = height-label_height
    white = display.create_pen(255,255,255)
    black = display.create_pen(0,0,0)

    centerbox(display=display, x=0,      y=0,     width=label_width, height=label_height, text=b, textpen=black, clearpen=white)
    centerbox(display=display, x=axleft, y=0,     width=label_width, height=label_height, text=a, textpen=black, clearpen=white)
    centerbox(display=display, x=0,      y=xytop, width=label_width, height=label_height, text=y, textpen=black, clearpen=white)
    centerbox(display=display, x=axleft, y=xytop, width=label_width, height=label_height, text=x, textpen=black, clearpen=white)

def ChooseItem(display, data, initial=0):
    inset = 0
    top = 30
    left = 0
    right = 0
    bottom = 30
    WIDTH, HEIGHT = display.get_bounds()
    labels(display=display, width=WIDTH, height=HEIGHT, b='Cancel', a='Save', y='Up', x='Down')
    box = Listbox(display=display, items=data, x=left, y=inset+top, width=WIDTH-(left+right), height=HEIGHT-(top+bottom))
    if (box.selected != initial):
        box.select(initial)

    box.draw()
    while True or KeyboardInterrupt:
        if button_x.read():
            box.down()
        if button_y.read():
            box.up()
        if button_b.read():
            return (false, initial)
        if button_a.read():
            return (true, box.selected)

    
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
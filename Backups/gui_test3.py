import gc
from picogui import PicoGUI, ChooseItem, ChooseVal
from servo import Servo

s = Servo(0)
s.enable()
servolimit = 30
wings_open_pos = 0.54
wings_closed_pos = 1.0

def move_wings(position):
    """
    Move the wings to a known position.
    
    Arguments:
    position - Location to move wings to (0=closed, servolimit= fully open)
    """
    pos = wings_closed_pos - ((position / servolimit) * (wings_closed_pos-wings_open_pos))
    print(f'Wing_Position: {pos}')
    s.to_percent(pos)
    

def cv_callback(picogui, val):
    print(f'Callback: {val}')
    move_wings(val)

gc.collect()

picogui = PicoGUI()

picogui.clear()

move_wings(0)

data = ['Apple', 'Pear', 'Giraffe', 'Polo','t1','t2','t3','t4','t5','t6','t7','t8','t9','t10','t11','t12','t13']
while True or KeyboardInterrupt:
    selected, value = ChooseItem(picogui=picogui, data=data, initial=1)
    if selected:
        print(f'Selected: {data[value]}')
    else:
        print(f'Cancelled: {data[value]}')

    selected, value = ChooseVal(picogui=picogui, title='Pick Number', initial=5, limit_high=servolimit, callback=cv_callback)
    if selected:
        print(f'Selected: {value}')
    else:
        print(f'Cancelled: {value}')

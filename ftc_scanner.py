import network
import binascii
import _thread
from picogui import PicoGUI, ChooseVal, Listbox, hsv_to_rgb
from time import sleep
from pimoroni import RGBLED, Button
import gc
from arms import Arms
import math
import utime
from config import Config
from neopixel import Neopixel

number_leds = 8
led_strip = Neopixel(number_leds, 0, 28, "GRB")

# Note:
# pimoroni libraries at https://github.com/pimoroni/pimoroni-pico

gc.collect()

picogui = PicoGUI()
config = Config()
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

picogui.clear()

s = Arms(0)
s.enable()
s.closed_value = config.get_var("arm0", 87)/100
s.open_value = config.get_var("arm1", 54)/100

led = RGBLED(6, 7, 8)
led.set_rgb(0, 0, 0)

LOGO_FILENAME = 'splash.jpg'


def show_memory(where):
    mem_free = gc.mem_free()
    mem_alloc = gc.mem_alloc()
    #print(f'{where}: Free={mem_free} Alloc={mem_alloc}')


def scan_single(ssid, bssid, channel):
    #print('Start Scan')
    wifi_list = wlan.scan()
    #print('End Scan')

    for hotspot in wifi_list:
        w_ssid = str(hotspot[0].decode('utf-8'))
        w_bssid = str(binascii.hexlify(hotspot[1]).decode('utf-8'))
        w_channel = str(hotspot[2])
        w_strength = str(hotspot[3])
        w_security = str(hotspot[4])
    #    print(
    #        f'Single: {ssid} {bssid} Chan:{channel} Strength: {hotspot[3]} Security: {hotspot[4]}')
        if ssid == w_ssid and w_bssid == bssid:
            return [w_ssid, w_bssid, w_channel, w_security, w_strength]
    return []

def find_insert_pos(list, ssid, strength):
    # TODO Implement watch to put at start of list
    for pos in range(0, len(list)):
        if list[pos][3] >= strength:
            return pos
    return len(list)+1

def scan_wifi(listbox):
    """ scan for wifi hotspots, returns a list of hotspots and their details """

    # scan returns: ssid, bssid, channel, security, strength
    # Note that the results from scan are inconsistent
    # https://github.com/micropython/micropython/issues/10017
    # [0] is the ssid
    # [1] is the binary bssid
    # [2] is the channel
    # [3] is the RSSI
    # [4] is a bitmask of security type 0x01 = WEP 0x02=WPA  0x04=WPA2
    # [5] is either not there, the number of times the SSID was found, a hardcoded 1 or is_hidden so we can ignore it.
    wifi_list = wlan.scan()
    wifi_map = {}
    # Step 1 - build a map of unique SSID entries
    for hotspot in wifi_list:
        ssid = str(hotspot[0].decode('utf-8'))
        #if len(ssid) > 16:
        #    ssid = ssid[:16]
        bssid = str(binascii.hexlify(hotspot[1]).decode('utf-8'))
        channel = str(hotspot[2])
        strength = str(hotspot[3])
        security = str(hotspot[4])
        if (ssid in wifi_map) and (wifi_map[ssid][3] < strength):
            wifi_map[ssid][4] += 1
        else:
            wifi_map[ssid] = [bssid, channel, security, strength,1]
    # Step 2 - build the ordered new list of items
    new_wifi = []
    for key in wifi_map:
        value = wifi_map[key]
        # We need to find where to insert the item in the list
        pos = find_insert_pos(new_wifi, ssid, value[3])
        if pos >= len(new_wifi):
            #                ssid  bssid     channel   strength  security  count     notseen
            new_wifi.append([key, value[0], value[1], value[2], value[3], value[4], 1])
        else:
            new_wifi.insert(pos, [key, value[0], value[1], value[2], value[3], value[4], 1])
        if len(new_wifi) > 50:
            new_wifi = new_wifi[:50]
    gc.collect()            
    # Dump the list
    #print('Step 2 list')
    #for key in range(0, len(new_wifi)):
    #    value = new_wifi[key]
    #    print(f'{key}, {value[0]}, {value[1]}, {value[2]}, {value[3]}, {value[4]}, {value[5]}') 
    # Step 3 - Merge the old list into the new list
    for key in range(0, len(listbox.data)):
        value = listbox.data[key]
        # See if we already have this
        if (value[6] < 30) and (len(new_wifi) < 50) and (value[0] not in wifi_map):
            # We don't so figure out where to add it
            pos = find_insert_pos(new_wifi, value[0], value[4])
            if pos >= len(new_wifi):
                #                ssid      bssid     channel   strength  security  count     notseen
                new_wifi.append([value[0], value[1], value[2], value[3], value[4], value[5], value[6]+1])
            else:
                new_wifi.insert(pos, [value[0], value[1], value[2], value[3], value[4], value[5], value[6]+1])
    # We need to keep the selected item set
    selected = listbox.selected
    ssidfind = ""
    if selected > len(listbox.data):
        ssidfind = listbox.data[selected][0]
    # Go through the entries
    for slot in range(0, len(new_wifi)):
        if new_wifi[slot][0] == ssidfind:
            listbox.selected = slot
            break
    #print('final list')
    #for key in range(0, len(new_wifi)):
    #    value = new_wifi[key]
    #    print(f'{key}, {value[0]}, {value[1]}, {value[2]}, {value[3]}, {value[4]}, {value[5]}')
    # Finally replace the list
    listbox.data = new_wifi

def set_arms(strength):
    global led_strip
    white = (70, 70, 70)
    black = (0, 0, 0)
    
    armclose = config.get_var("arm0", 87)/100
    armopen = config.get_var("arm1", 54)/100
    armdb0 = -config.get_var("adb0", 60)
    armdb1 = -config.get_var("adb1", 50)
    armdb2 = -config.get_var("adb2", 40)
    armdb3 = -config.get_var("adb3", 30)
    lightdb0 = -config.get_var("ldb0", 45)
    lightdb1 = -config.get_var("ldb1", 42)
    lightdb2 = -config.get_var("ldb2", 39)
    lightdb3 = -config.get_var("ldb3", 36)
    lightdb4 = -config.get_var("ldb4", 33)
    lightdb5 = -config.get_var("ldb5", 30)

    # Lets move the arms to the right place
    if strength != 0:
        to = 0
        pct = 0
        if strength <= armdb0:
            to = armclose
            s.close_arms()
        elif strength >= armdb3:
            to = armopen
            s.open_arms()
        elif strength <= armdb1:
            pct = 0.1*((strength-armdb0)/(armdb1-armdb0))
            to = armclose-((armclose-armopen)*pct)
            s.to_percent(to)
        elif strength <= armdb2:
            pct = 0.1+(0.4*((strength-armdb1)/(armdb2-armdb1)))
            to = armclose-((armclose-armopen)*pct)
            s.to_percent(to)
        else:
            pct = 0.5+(0.5*((strength-armdb2))/(armdb3-armdb2))
            to = armclose-((armclose-armopen)*pct)
            s.to_percent(to)
        #print(f'pct={pct} to={to} Strength={strength} [{armdb0},{armdb1},{armdb2},{armdb3}]')

        # figure out the lights
        lights = 0
        if strength >= lightdb0:
            if strength >= lightdb5:
                lights = 5
            elif strength >= lightdb4:
                lights = 4
            elif strength >= lightdb3:
                lights = 3
            elif strength >= lightdb2:
                lights = 2
            elif strength >= lightdb1:
                lights = 1
        if lights >= 1:
            led_strip.set_pixel(0, white)
            led_strip.set_pixel(4, white)
        else:
            led_strip.set_pixel(0, black)
            led_strip.set_pixel(4, black)
        if lights >= 2:
            led_strip.set_pixel(1, white)
            led_strip.set_pixel(5, white)
        else:
            led_strip.set_pixel(1, black)
            led_strip.set_pixel(5, black)
        if lights >= 3:
            led_strip.set_pixel(2, white)
            led_strip.set_pixel(6, white)
        else:
            led_strip.set_pixel(2, black)
            led_strip.set_pixel(6, black)
        if lights >= 4:
            led_strip.set_pixel(3, white)
            led_strip.set_pixel(7, white)
        else:
            led_strip.set_pixel(3, black)
            led_strip.set_pixel(7, black)
        led_strip.show()
        #print(f'Lights={lights} [{lightdb0},{lightdb1},{lightdb2},{lightdb3},{lightdb4},{lightdb5}]')



def sparkle_led():
    """ makes the LED sparkle """
    for hue in range(0, 100, 1):
        r, g, b = hsv_to_rgb(hue/100, 1.0, 1.0)
        led.set_rgb(r, g, b)
        sleep(0.01)


def rgb_green():
    """ sets the LED to green """
    led.set_rgb(0, 255, 0)


def flash_yellow(times):
    """ flashes the LED yellow, for the number of items specified """
    for _ in range(1, times):
        led.set_rgb(255, 255, 0)
        sleep(0.5)
        led.set_rgb(0, 0, 0)
        sleep(0.5)


def map_range(value, low1, high1, low2, high2):
    """ maps a value from one range to another """
    return low2 + (high2 - low2) * (value - low1) / (high1 - low1)


def db_to_percent(selected_item, full_list) -> float:
    """ Returns the percentage, based on the signal strength """
    item = full_list[selected_item]
    signal = int(item[6])
    return map_range(signal, 0, 100, 0, -100) / 100


def clip(value, min_clip, max_clip) -> float:
    """ Checks if the value with within the min or max and
    ensures the value stays within the min max range """
    if value < min_clip:
        return min_clip
    if value > max_clip:
        return max_clip
    return value


def start_up():
    # Draw logo
    show_memory('Startup')

    s.close_arms()
    picogui.draw_jpg(filename=LOGO_FILENAME)
    for strength in range(0,50):
        set_arms(strength-70)
        sleep(0.04)
    for strength in range(0,50):
        set_arms(-20-strength)
        sleep(0.03)
    set_arms(-99)
    s.disable()

def settingrender(picogui, item, x, y):
    """
      Callback function to display the settings data
      item = [settingid, title, value]
    """
    picogui.display.text(item[1], x, y)
    picogui.display.text(str(item[2]), x+200, y)

def cv_callback(picogui, val):
    #print(f'Callback: {val}')
    s.to_percent(val/100)

def SettingsMenu(picogui):
    settings_list = [['rescan', 'Rescan time', 0],
                     ['adb0', 'Arm DB Closed', 0],
                     ['adb1', 'Arm DB 10%', 0],
                     ['adb2', 'Arm DB 50%', 0],
                     ['adb3', 'Arm DB Full', 0],
                     ['ldb0', 'Lights DB Off', 0],
                     ['ldb1', 'Lights DB 1', 0],
                     ['ldb2', 'Lights DB 2', 0],
                     ['ldb3', 'Lights DB 3', 0],
                     ['ldb4', 'Lights DB 4', 0],
                     ['ldb5', 'Lights DB Flashing', 0],
                     ['arm0', 'Arm Closed Position', 0],
                     ['arm1', 'Arm Open Position', 0],
                     ]
    redraw = True
    no_of_settings = len(settings_list)
    for line in range(0, no_of_settings):
        settings_list[line][2] = config.get_var(settings_list[line][0], 50)
    inset = 0
    top = 30
    left = 0
    right = 0
    bottom = 30
    selected = 0
    height = picogui.display_height-(top+bottom)
    width = picogui.display_width-(left+right)
    box = Listbox(picogui, items=settings_list, x=left, y=inset +
                  top, width=width, height=height, renderfunc=settingrender)

    while True or KeyboardInterrupt:
        if redraw:
            picogui.clear()
            picogui.labels(b="Home", a="Select")
            box.selected = selected
            box.draw()
            redraw = False

        if picogui.button_x.read():
            box.down()
        if picogui.button_y.read():
            box.up()
        if picogui.button_a.read():
            #print(f'Selected item')
            item = settings_list[box.selected]

            callback = None
            if item[0] == 'arm0' or item[0] == 'arm1':
                callback = cv_callback
            updated, value = ChooseVal(
                picogui=picogui, title=item[1], initial=item[2], limit_high=100, callback=callback)
            if updated:
                selected = box.selected
                config.set_var(item[0], value)
                item[2] = value
                redraw = True
                s.closed_value = config.get_var("arm0", 87)/100
                s.open_value = config.get_var("arm1", 54)/100
                #print(f'Setting {item[0]} = {value}')

        if picogui.button_b.read():
            return


def TrackWifi(picogui, item):
    """
    item = [ssid, bssid, channel, security, strength]
    Menu buttons B=Home  A=Enable/Disable Arms
                 Y=Watch/Normal  X=Hide/Unhide
    """
    security_type = {'0': 'Open',
                     '1': 'WEP-PSK',
                     '2': 'WPA',
                     '3': 'WPA/WEP-PSK',
                     '4': 'WPA2',
                     '5': 'WPA2/WEP-PSK',
                     '6': 'WPA2/WPA',
                     '7': 'WPA2/WPA/WEP-PSK',
                     }

    top = 30
    left = 0
    right = 0
    bottom = 30
    inset = 10
    height = picogui.display_height-(top+bottom)
    width = picogui.display_width-(left+right)
    bartop = 180
    barleft = picogui.display_width-15
    barwidth = 10
    barheight = 100
    redraw = True
    hidden = False
    arms = True
    watch = False
    start_time = utime.ticks_ms()
    history = []

    s.enable()

    while True or KeyboardInterrupt:
        if redraw:
            picogui.clear()
            # Determine all the labels to put up
            status_text = ""
            ylabel = "Watch"
            if watch:
                ylabel = "Normal"
                status_text = "**WATCHING**"
            xlabel = "Hide"
            if hidden:
                xlabel = "Unhide"
                status_text = "**IGNORED**"
            alabel = "Arms Move"
            if arms:
                alabel = "Arms Stop"
            picogui.labels(b="Home", a=alabel, y=ylabel, x=xlabel)
            ssid = item[0]
            if len(ssid) > 20:
                ssid = ssid[:20]
            # Clear out the center area where we will render everything
            picogui.rect(x=left, y=top, width=width,
                         height=height, pen=picogui.whitepen)
            # Display the SSID
            picogui.centertext(
                text=ssid, x=left, y=top+(picogui.item_height), width=width)
            # Display the BSSID
            picogui.text(text="BSSID:  "+item[1][:6]+'-'+item[1][6:], x=left+inset,
                         y=top+(picogui.item_height*3), pen=picogui.blackpen)
            # Display the Channel
            picogui.text(text="Channel: "+item[2], x=left+inset,
                         y=top+(picogui.item_height*4), pen=picogui.blackpen)
            # Display the Security Level
            picogui.text(text=security_type[item[3]], x=left+inset,
                         y=top+(picogui.item_height*5), pen=picogui.blackpen)
            # If we are watching or ignoring it, display it
            picogui.text(text=status_text, x=left+inset,
                         y=top+(picogui.item_height*6), pen=picogui.blackpen)
            # Display the current Strength
            picogui.text(item[4], x=barleft-20,
                         y=bartop-(picogui.item_height+5), pen=picogui.blackpen)
            # Let's show a bar
            picogui.box(x=barleft, y=bartop, width=barwidth, height=barheight)
            strength = int(item[4])
            if strength != 0:
                # <= -80 = Red
                # <= -70 = orange
                # <= -60 = Yellow
                # Eveything else is green
                pen = picogui.greenpen
                if strength <= -80:
                    pen = picogui.redpen
                elif strength <= -70:
                    pen = picogui.orangepen
                elif strength <= -60:
                    pen = picogui.yellowpen
                graphheight = 100+strength
                picogui.rect(x=barleft+1, y=bartop+1-strength,
                             width=barwidth-1, height=99+strength, pen=pen)
            # And a graph
            graphwidth = barleft-(inset*2)
            picogui.box(x=inset, y=bartop, width=graphwidth, height=barheight)
            if len(history) >= (graphwidth-1):
                history.pop()
            history.insert(0, -strength)
            picogui.display.set_pen(picogui.blackpen)
            for pos in range(0, len(history)):
                col = inset+(graphwidth-1)-pos
                row = bartop+history[pos]
                picogui.display.line(col, row, col, row+4)

            picogui.update()
            set_arms(strength)
            gc.collect()
            show_memory('After redraw')
            redraw = False

        if picogui.button_y.read():
            # Mark it as watch
            watch = not watch
            if watch:
                hidden = False
            redraw = True
        if picogui.button_x.read():
            # Mark it as Ignore
            hidden = not hidden
            if hidden:
                watch = False
            redraw = True

        if picogui.button_b.read():
            set_arms(-99)
            s.close_arms()
            s.disable()
            return

        if picogui.button_a.read():
            arms = not arms
            redraw = True

        # See if it is time for us to refresh the Wifi list
        end_time = utime.ticks_ms()
        elapsed_time = utime.ticks_diff(end_time, start_time)
        if elapsed_time > 250:
            new_item = scan_single(
                ssid=item[0], bssid=item[1], channel=item[2])
            if len(new_item) > 0:
                item = new_item
            else:
                item[4] = "0"
            start_time = end_time
            redraw = True

def wifirender(picogui, item, x, y):
    """
      Callback function to display the Wifi Scan Data
      item = [ssid, bssid, channel, security, strength]
    """
    ssid = item[0]
    if len(ssid) > 16:
        ssid = ssid[:16]
    picogui.display.text(ssid, x, y)
    picogui.display.text(item[2], x+180, y)
    picogui.display.text(item[4], x+200, y)


def WifiMenu(picogui):
    inset = 0
    top = 30
    left = 0
    right = 0
    bottom = 30
    height = picogui.display_height-(top+bottom)
    width = picogui.display_width-(left+right)
    selected = 0
    redraw = True
    rescan = True
    ssid_list = []
    box = Listbox(picogui, items=ssid_list, x=left, y=inset+top,
                  width=width, height=height, renderfunc=wifirender)
    start_time = utime.ticks_ms()
    show_memory('in WifiMenu')
    rescan_time = config.get_var("rescan", 0)*100
    
    while True or KeyboardInterrupt:
        if redraw or rescan:
            if rescan:
                rescan = False
                rescan_time = config.get_var("rescan", 0)*100
                show_memory('before rescan')
                scan_wifi(box)
                gc.collect()
                box.draw()
                gc.collect()
                show_memory('After rescan')
            redraw = False
            picogui.clear()
            picogui.labels(b="Settings", a="Select")
            box.draw()

        if picogui.button_x.read():
            box.down()
        if picogui.button_y.read():
            box.up()
        if picogui.button_b.read():
            SettingsMenu(picogui)
            rescan = True
        if picogui.button_a.read():
            TrackWifi(picogui, box.data[box.selected])
            s.close_arms()
            redraw = True

        # See if it is time for us to refresh the Wifi list
        end_time = utime.ticks_ms()
        elapsed_time = utime.ticks_diff(end_time, start_time)
        
        if rescan_time > 0 and elapsed_time > rescan_time:
            rescan = True
            start_time = utime.ticks_ms()

start_up()
show_memory('Before Wifi')
gc.collect()
show_memory('After GC')
WifiMenu(picogui)

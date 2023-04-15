from config import Config
from picogui import PicoGUI, ChooseItem, ChooseVal
        
picogui = PicoGUI()
config = Config()
arm1 = config.get_var('arm1', 10)

selected, value = ChooseVal(picogui=picogui, title='Set Arm Number', initial=arm1, limit_high=50)

if selected:
    config.set_var('arm1', value)

from picogui import PicoGUI, ChooseItem, ChooseVal
import ujson

class Config():
    config = {}
    def __init__(self):
        self.config = self.read_config()
        
    def read_config(self):
        try:
            with open('config.json', 'r') as f:
                return ujson.load(f)
        except:
            return {}

    def save_config(self):
        with open('config.json', 'w') as f:
            ujson.dump(self.config, f)
    
    def set_var(self, var, val):
        self.config[var]=val
        self.save_config()
    
    def remove_var(self, var):
        del self.config[var]
        
    def get_var(self, var, default_val):
        if var in self.config:
            return self.config[var]
        return default_val

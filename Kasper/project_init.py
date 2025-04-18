import time
import random
from machine import Pin, I2C  # type: ignore
from ssd1306 import SSD1306_I2C  # type: ignore

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

SW0 = Pin(9, Pin.IN, Pin.PULL_UP)
SW1 = Pin(8, Pin.IN, Pin.PULL_UP)
SW2 = Pin(7, Pin.IN, Pin.PULL_UP)

ROTA = Pin(10, Pin.IN, Pin.PULL_UP)
ROTB = Pin(11, Pin.IN, Pin.PULL_UP)
ROT_push = Pin(12, Pin.IN, Pin.PULL_UP)

class Menu:
    def __init__(self, options, title="Menu"):
        self.options = options
        self.title = title
        pass
    
    def scroll(self, direction):
        if direction == -1:
            self.options.insert(0, self.options.pop())
        elif direction == 1:
            self.options.append(self.options.pop(0))
    
    def option_select(self, option):
        if option == "MEASURE HR":
            print("Measure HR")
        elif option == "BASIC ANALYSIS":
            print("Basic Analysis")
        elif option == "KUBIOS":
            print("Kubios")
        elif option == "HISTORY":
            print("History")
    
    def display(self):
        oled.fill(0)
        oled.text(">", 0, 20)
        oled.text(f"{self.title}", 0, 0)
        for option in range(len(self.options)):
            oled.text(f"{self.options[option]}",10, 20 + option * 10)
             
        oled.show()

    def run(self):
        while True:
            if not SW2.value():
                self.scroll(-1)
            if not SW0.value():
                self.scroll(1)
            if not SW1.value():
                break
            if not ROT_push.value():
                self.option_select(self.options[0])
            self.display()
            time.sleep(0.1)

    

            
menu = Menu(["MEASURE HR", "BASIC ANALYSIS", "KUBIOS", "HISTORY"], "Beat Buddy")

menu.run()
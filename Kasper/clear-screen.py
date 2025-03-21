import time 
from machine import UART, Pin, I2C, Timer, ADC 
from ssd1306 import SSD1306_I2C 
SW0 = Pin(9, Pin.IN, Pin.PULL_UP) 
SW1 = Pin(8, Pin.IN, Pin.PULL_UP) 
SW2 = Pin(7, Pin.IN, Pin.PULL_UP) 
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128 
oled_height = 64 
oled = SSD1306_I2C(oled_width, oled_height, i2c) 

oled.fill(0)
oled.show()
from machine import Pin, I2C 
from ssd1306 import SSD1306_I2C 

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128 
oled_height = 64 
oled = SSD1306_I2C(oled_width, oled_height, i2c) 

oled.fill(0)
oled.show()
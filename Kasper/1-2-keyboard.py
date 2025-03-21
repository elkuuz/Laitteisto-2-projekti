import time
from machine import Pin, I2C # type: ignore
from ssd1306 import SSD1306_I2C # type: ignore

SW0 = Pin(9, Pin.IN, Pin.PULL_UP)
SW1 = Pin(8, Pin.IN, Pin.PULL_UP)
SW2 = Pin(7, Pin.IN, Pin.PULL_UP)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

oled.fill(0)
oled.show()


line_height = 10  
max_lines = oled_height // line_height  
lines = []  

print("Type your input below:")

while True:
    
    user_input = input("> ")
    
    lines.append(user_input)

    if len(lines) > max_lines:
        lines.pop(0)
        
    oled.fill(0)

    for i, line in enumerate(lines):
        oled.text(line, 0, i * line_height)
        
    oled.show()
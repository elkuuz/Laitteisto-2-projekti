import time
from machine import Pin, I2C # type: ignore
from ssd1306 import SSD1306_I2C # type: ignore

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

SW0 = Pin(9, Pin.IN, Pin.PULL_UP)
SW1 = Pin(8, Pin.IN, Pin.PULL_UP)
SW2 = Pin(7, Pin.IN, Pin.PULL_UP)

middle_y = oled_height // 2
x = 0
y = middle_y

oled.fill(0)
oled.show()

while True:
    if not SW2.value():
        y = max(0, y - 1)
    if not SW0.value():
        y = min(oled_height - 1, y + 1)
    if not SW1.value():
        oled.fill(0)
        x = 0
        y = middle_y

    oled.pixel(x, y, 1)
    oled.show()

    x += 1
    if x >= oled_width:
        x = 0

    time.sleep(0.01)

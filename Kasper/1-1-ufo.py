import time
from machine import UART, Pin, I2C, Timer, ADC # type: ignore
from ssd1306 import SSD1306_I2C # type: ignore
button_3 = Pin(9, Pin.IN, Pin.PULL_UP)
button_2 = Pin(8, Pin.IN, Pin.PULL_UP)
button_1 = Pin(7, Pin.IN, Pin.PULL_UP)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

ufo = "<=>"
position = 50
speed = 1

while True:

    oled.fill(0)
    oled.text(ufo, position, 55)
    oled.show()

    if button_1.value() == 0:

        position -= speed

        if position < -1:
            position = -1

    if button_3.value() == 0:

        position += speed

        if position > 105:
            position = 105

    if button_2.value() == 0:

        oled.fill(0)
        oled.text("Game Over", 20, 20)
        oled.show()

        time.sleep(2)

        oled.fill(0)
        oled.show()
        break
# ill try to use classes this time
# Features: level select, easy way to load and create levels
# only 3 buttons 
# 3 levels

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

last_state = (ROTA.value(), ROTB.value())
counter = 0

def update_encoder(pin):
    global last_state, counter
    global player_pos
    current_a = ROTA.value()
    current_b = ROTB.value()
    new_state = (current_a, current_b)

    # Detect direction based on state transitions
    if last_state == (0, 1) and new_state == (0, 0):
        counter += 1  # Clockwise
        player_pos += 1
    elif last_state == (1, 0) and new_state == (0, 0):
        counter -= 1  # Counter-clockwise
        player_pos -= 1

    # Ensure player_pos stays within valid range
    if player_pos < 0:
        player_pos = 0
    elif player_pos > 3:
        player_pos = 3

    last_state = new_state

# Attach interrupts to both pins
ROTA.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=update_encoder)
ROTB.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=update_encoder)



player = "v"
note_hit_zones = {0: 35, 1: 51, 2: 67, 3: 83}
player_pos = 0
while True:
    oled.fill(0)

    oled.text(player, note_hit_zones[player_pos], 48)
    oled.text("_ _ _ _", 35, 50)
    oled.show()
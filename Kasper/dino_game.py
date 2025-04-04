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

floor = "__________________"
dino = "R"
enemy_air = "B"
enemy_ground = "K"

dino_pos = [0, 54]
dino_death = [0]

enemy_list = []

air_time = 6
in_air = False

enemy_interval = 50

score = 0

def enemy_movement():
    for enemy in enemy_list:
        enemy['x'] -= 1
        collision()
        if enemy['x'] < 0:
            enemy_list.remove(enemy)
        else:
            oled.text(enemy["enemy"], enemy['x'], enemy['y'])

def jump_up(in_air):
    in_air = True
    for i in range(0, 6):
        oled.fill(0)
        oled.text(floor, 0, 56)
        oled.text(dino, dino_pos[0], dino_pos[1] - i)
        dino_pos[1] -= i
        enemy_movement()
        oled.show()
    return in_air

def jump_down():
    for i in range(0, 6):
        oled.fill(0)
        oled.text(floor, 0, 56)
        oled.text(dino, dino_pos[0], dino_pos[1] + i)
        dino_pos[1] += i
        enemy_movement()
        oled.show()

def collision():
    for enemy in enemy_list:
        enemy_hitbox_x = range(enemy['x'] - 4, enemy['x'] + 4)
        enemy_hitbox_y = range(enemy['y'] - 6, enemy['y'] + 6)
        if dino_pos[0] in enemy_hitbox_x and dino_pos[1] in enemy_hitbox_y:
            print("You died")
            dino_death[0] = 1
            break

while True:
    oled.text("Score: " + str(score), 0, 0)
    if in_air:
        air_time -= 1
    if in_air == False and ROT_push.value() == 0:
        in_air = jump_up(in_air)

    if air_time <= 0:
        air_time = 6
        in_air = False
        jump_down()

    if enemy_interval == 0:
        enemy_interval = random.randint(25, 75)
        if random.randint(0, 1) == 0:
            enemy_list.append({"enemy": enemy_air, "x": 128, "y": 40})
        else:
            enemy_list.append({"enemy": enemy_ground, "x": 128, "y": 54})
            
    oled.fill(0)

    for i in enemy_list:
        pass
    
    enemy_movement()
    
    if dino_death[0] == 1:
        break
    
    oled.text(dino, dino_pos[0], dino_pos[1])
    oled.text(floor, 0, 56)
    oled.text("Score: " + str(score), 0, 0)
    oled.show()

    enemy_interval -= 1
    score += 1


oled.fill(0)
oled.text("You died", 20, 20)
oled.text("Score: " + str(score), 20, 30)
oled.show()

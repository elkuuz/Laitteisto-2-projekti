import time, random
from machine import Pin, I2C # type: ignore
from ssd1306 import SSD1306_I2C # type: ignore
button_3 = Pin(9, Pin.IN, Pin.PULL_UP)
button_2 = Pin(8, Pin.IN, Pin.PULL_UP)
button_1 = Pin(7, Pin.IN, Pin.PULL_UP)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

ROTA = Pin(10, Pin.IN, Pin.PULL_UP)
ROTB = Pin(11, Pin.IN, Pin.PULL_UP)
# Initialize variables

ROT_push = Pin(12, Pin.IN, Pin.PULL_UP)



ufo = "<=>"
enemy = "V"
bullet = "|"

position = 50
speed = 5
score = 0
enemy_interval = 1
enemy_movement_cooldown = 40
difficulty_changed = 0

bullets = []
enemy_list = []

gaming = True

def update_encoder(pin):
    global last_state, counter
    global position, speed
    current_a = ROTA.value()
    current_b = ROTB.value()
    new_state = (current_a, current_b)

    # Detect direction based on state transitions
    if last_state == (0, 1) and new_state == (0, 0):
        counter += 1  # Clockwise
        position += speed

        if position > 105:
            position = 105
    elif last_state == (1, 0) and new_state == (0, 0):
        counter -= 1  # Counter-clockwise
        position -= speed

        if position < -1:
            position = -1
    last_state = new_state

# Attach interrupts to both pins
ROTA.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=update_encoder)
ROTB.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=update_encoder)

last_state = (ROTA.value(), ROTB.value())
counter = 0

while gaming:

    oled.fill(0)
    oled.text(ufo, position, 55)
    
    for b in bullets:
        b['y'] -= 1
        if b['y'] < 0:
            bullets.remove(b)
        else:
            oled.text(bullet, b['x'], b['y'])
        if b in bullets:
            for e in enemy_list:
                enemy_hitbox_x = range(e['x'] - 4, e['x'] + 4)
                enemy_hitbox_y = range(e['y'], e['y'] + 6) 
                if b['x'] in enemy_hitbox_x and b['y'] in enemy_hitbox_y:
                    bullets.remove(b)
                    enemy_list.remove(e)
                    score += 1
                    if score == 5:
                        difficulty_changed = 1
                    elif score == 15:
                        difficulty_changed = 1
                    elif score == 25:
                        difficulty_changed = 1
                    elif score == 40:
                        difficulty_changed = 1
                    elif score == 50:
                        difficulty_changed = 1
                    if difficulty_changed == 1:
                        oled.text('SPEED UP', 45, 20)
                        oled.show()
                        time.sleep(1.5)
                        difficulty_changed = 0
                    break
    
    oled.text('S:' + str(score), 0, 0)
    
    for e in enemy_list:
        e['cooldown'] -= 1
        if e['cooldown'] == 0:
            e['y'] += 8
            e['cooldown'] = 40
        if e['y'] >= 60:
            gaming = False
            break
        else:
            oled.text(enemy, e['x'], e['y'])
        enemy_movement_cooldown = 40
    
    if gaming == False:
        break
    
    oled.show()
    

    if button_1.value() == 0:
        bullets.append({'x': position + 8, 'y': 54})
        time.sleep(0.2)
   
    if enemy_interval <= 0:
        enemy_list.append({'x': random.randrange(15,115), 'y': 0, 'cooldown': 40})
        if score < 5:
            enemy_interval = 150
        elif score >= 5 and score < 15:
            enemy_interval = 125
        elif score >= 15 and score < 25:
            enemy_interval = 100
        elif score >= 25 and score < 40:
            enemy_interval = 75
        elif score >= 40 and score < 50:
            enemy_interval = 50
        elif score >= 50:
            enemy_interval = 25

    enemy_interval -= 1
    
oled.fill(0)
oled.text("Game Over", 25, 20)
oled.text("Score: " + str(score), 25, 30)
oled.show()
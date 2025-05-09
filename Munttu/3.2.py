import time
from fifo import Fifo
from machine import Pin

class Encoder:
    def __init__(self, rot_a, rot_b, rot_push):
        self.a = Pin(rot_a, mode=Pin.IN, pull=Pin.PULL_UP)
        self.b = Pin(rot_b, mode=Pin.IN, pull=Pin.PULL_UP)
        self.p = Pin(rot_push, mode=Pin.IN, pull=Pin.PULL_UP)

        self.fifo = Fifo(50, typecode='i')

        self.a.irq(handler=self.turn_handler, trigger=Pin.IRQ_RISING, hard=True)
        self.p.irq(handler=self.button_handler, trigger=Pin.IRQ_FALLING, hard=True)

        self.last_press_time = time.ticks_ms()

    def turn_handler(self, pin):
        if self.b.value():
            self.fifo.put(1)  # Clockwise
        else:
            self.fifo.put(-1)  # Counter-clockwise

    def button_handler(self, pin):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_press_time) > 350:
            self.fifo.put(0)  # Button press event
            self.last_press_time = now

# Set up encoder and LEDs
encoder = Encoder(10, 11, 12)
led_pins = [Pin(20, Pin.OUT), Pin(21, Pin.OUT), Pin(22, Pin.OUT)]
led_states = [False, False, False]
menu_index = 0
menu_items = ["LED1", "LED2", "LED3"]

# Menu rendering
def render_menu():
    print("\033[2J\033[H")  # Clear terminal
    for i, item in enumerate(menu_items):
        selector = ">" if i == menu_index else " "
        state = "ON" if led_states[i] else "OFF"
        print(f"{selector} {item} [{state}]")

render_menu()

while True:
    if encoder.fifo.has_data():
        event = encoder.fifo.get()
        if event == 1:
            menu_index = (menu_index + 1) % len(menu_items)
            render_menu()
        elif event == -1:
            menu_index = (menu_index - 1) % len(menu_items)
            render_menu()
        elif event == 0:
            led_states[menu_index] = not led_states[menu_index]
            led_pins[menu_index].value(led_states[menu_index])
            render_menu()

    time.sleep(0.01)
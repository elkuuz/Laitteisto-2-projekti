import time
from fifo import Fifo  
from machine import Pin, PWM  # Add PWM to the import statement

class Encoder:
    def __init__(self, rot_a, rot_b, rot_push, led):
        self.a = Pin(rot_a, mode=Pin.IN, pull=Pin.PULL_UP)
        self.b = Pin(rot_b, mode=Pin.IN, pull=Pin.PULL_UP)
        self.p = Pin(rot_push, mode=Pin.IN, pull=Pin.PULL_UP)
        self.led = PWM(Pin(led))
        self.led.freq(1000)  # Set frequency to 1kHz for PWM
        self.fifo = Fifo(50, typecode='i')
        self.a.irq(handler=self.handler, trigger=Pin.IRQ_RISING, hard=True)
        self.brightness = 0
        self.led_on = False

    def handler(self, pin):
        if self.b.value():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

    def debounce(self, pin):
        time.sleep(0.011)
        return pin.value()

rot = Encoder(10, 11, 12, 20)

while True:
    if not rot.debounce(rot.p):
        rot.led_on = not rot.led_on
        if rot.led_on:
            rot.led.duty_u16(rot.brightness)  # Set initial brightness
        else:
            rot.led.duty_u16(0)  # Turn off LED

    if rot.led_on and rot.fifo.has_data():
        value = rot.fifo.get()
        if value == 1:
            rot.brightness = min(rot.brightness + 150, 5535)  # Adjust for PWM range
        elif value == -1:
            rot.brightness = max(rot.brightness - 150, 10)
        rot.led.duty_u16(rot.brightness)  # Adjust LED brightness








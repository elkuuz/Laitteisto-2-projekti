from machine import Pin # type: ignore
import time

led = Pin("LED", Pin.OUT)
while True:
    led.toggle()
    time.sleep(1)
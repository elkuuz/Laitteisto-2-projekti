from machine import Pin, PWM
import time

# Initialize LED pin with PWM
led = PWM(Pin(21))
led.freq(1000)  # Set PWM frequency

# Test LED brightness
brightness = 32768  # 50% brightness
led.duty_u16(brightness)  # Set brightness
time.sleep(5)  # Keep LED on for 5 seconds

# Turn LED off
led.duty_u16(0)
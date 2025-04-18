import machine
import utime
from collections import deque

# Hardware setup
led = machine.PWM(machine.Pin(20))  # Assuming LED on GPIO15 with PWM
led.freq(1000)  # 1kHz PWM frequency
led.duty_u16(0)  # Start with LED off

# Rotary encoder pins (adjust according to your wiring)
encoder_clk = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_UP)
encoder_dt = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP)
encoder_sw = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)

# Encoder state variables
encoder_fifo = deque((), 32)  # FIFO for encoder events (max 32 events)
last_encoder_state = (encoder_clk.value() << 1) | encoder_dt.value()
encoder_debounce_time = utime.ticks_ms()

# Button debouncing variables
button_debounce_time = 0
button_last_state = encoder_sw.value()
button_pressed = False
DEBOUNCE_DELAY_MS = 50

# LED state variables
led_on = False
current_brightness = 32768  # 50% brightness initially (16-bit PWM)


# Encoder interrupt handler
def encoder_isr(pin):
    global last_encoder_state, encoder_debounce_time

    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, encoder_debounce_time) < 5:
        return  # Debounce

    new_state = (encoder_clk.value() << 1) | encoder_dt.value()

    # State transition table for quadrature decoding
    transitions = {
        0b00: {0b01: -1, 0b10: 1},
        0b01: {0b11: -1, 0b00: 1},
        0b11: {0b10: -1, 0b01: 1},
        0b10: {0b00: -1, 0b11: 1}
    }

    if new_state != last_encoder_state:
        direction = transitions.get(last_encoder_state, {}).get(new_state, 0)
        if direction != 0:
            encoder_fifo.append(direction)  # Add to FIFO (1 for CW, -1 for CCW)
        last_encoder_state = new_state
        encoder_debounce_time = current_time


# Set up interrupts
encoder_clk.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=encoder_isr)
encoder_dt.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=encoder_isr)

# Main loop
while True:
    # Handle button press (with debouncing)
    current_button_state = encoder_sw.value()
    current_time = utime.ticks_ms()

    if current_button_state != button_last_state:
        button_debounce_time = current_time
        button_last_state = current_button_state

    if (utime.ticks_diff(current_time, button_debounce_time) > DEBOUNCE_DELAY_MS and
            not button_pressed and current_button_state == 0):
        button_pressed = True
        led_on = not led_on  # Toggle LED state

        if led_on:
            led.duty_u16(current_brightness)
        else:
            led.duty_u16(0)

    if current_button_state == 1:
        button_pressed = False

    # Handle encoder turns if LED is on
    if led_on and len(encoder_fifo) > 0:
        direction = encoder_fifo.popleft()  # Get oldest event
        current_brightness += direction * 3276  # Adjust brightness by ~10%

        # Clamp brightness between 0 and 65535
        current_brightness = max(0, min(65535, current_brightness))
        led.duty_u16(current_brightness)

    utime.sleep_ms(10)  # Small delay to reduce CPU usage
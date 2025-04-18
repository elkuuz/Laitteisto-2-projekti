from machine import Pin, I2C
import ssd1306
import utime
from collections import deque

# Initialize I2C and OLED
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)  # Adjust pins for your setup
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Hardware setup
led_pins = [Pin(20, Pin.OUT), Pin(21, Pin.OUT), Pin(22, Pin.OUT)]
encoder_clk = Pin(10, Pin.IN, Pin.PULL_UP)
encoder_dt = Pin(11, Pin.IN, Pin.PULL_UP)
encoder_sw = Pin(12, Pin.IN, Pin.PULL_UP)

# State variables
menu_items = ["LED1", "LED2", "LED3"]
led_states = [False, False, False]
current_selection = 0
fifo = deque((), 32)  # FIFO for encoder events
last_encoder_state = (encoder_clk.value() << 1) | encoder_dt.value()
last_button_time = 0
DEBOUNCE_DELAY_MS = 200

# Interrupt handlers
def encoder_turn_isr(pin):
    global last_encoder_state
    new_state = (encoder_clk.value() << 1) | encoder_dt.value()
    transitions = {
        0b00: {0b01: -1, 0b10: 1},
        0b01: {0b11: -1, 0b00: 1},
        0b11: {0b10: -1, 0b01: 1},
        0b10: {0b00: -1, 0b11: 1}
    }
    if new_state != last_encoder_state:
        direction = transitions.get(last_encoder_state, {}).get(new_state, 0)
        if direction != 0:
            fifo.append(("turn", -direction))
        last_encoder_state = new_state

def encoder_button_isr(pin):
    global last_button_time
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_button_time) > DEBOUNCE_DELAY_MS:
        fifo.append(("press", None))
        last_button_time = current_time

# Attach interrupts
encoder_clk.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=encoder_turn_isr)
encoder_dt.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=encoder_turn_isr)
encoder_sw.irq(trigger=Pin.IRQ_FALLING, handler=encoder_button_isr)

# Helper functions
def render_menu():
    oled.fill(0)
    for i, item in enumerate(menu_items):
        prefix = "->" if i == current_selection else "  "
        state = "ON" if led_states[i] else "OFF"
        oled.text(f"{prefix} {item} [{state}]", 0, i * 16)
    oled.show()

def toggle_led(index):
    led_states[index] = not led_states[index]
    led_pins[index].value(led_states[index])

# Main program loop
render_menu()
while True:
    if fifo:
        event, value = fifo.popleft()
        if event == "turn":
            current_selection = (current_selection + value) % len(menu_items)
            render_menu()
        elif event == "press":
            toggle_led(current_selection)
            render_menu()
    utime.sleep_ms(10)
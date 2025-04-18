from machine import Pin, I2C, Timer, ADC
from ssd1306 import SSD1306_I2C
import time

# Initialize I2C and OLED
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize buttons
SW0 = Pin(9, Pin.IN, Pin.PULL_UP)  # Start/Stop button
SW1 = Pin(8, Pin.IN, Pin.PULL_UP)  # Reserved for future use
SW2 = Pin(7, Pin.IN, Pin.PULL_UP)  # Reserved for future use

# Initialize ADC for heart rate sensor
adc = ADC(Pin(27))  # Using GPIO pin 27 for ADC1

# Variables to track state
measuring = False
bpm = 0
last_beat_time = 0
threshold = 500  # Adjust this threshold based on your sensor's output
beat_times = []

# Function to display the start menu
def display_start_menu():
    oled.fill(0)
    oled.text("Press Start to", 0, 16)
    oled.text("measure", 0, 32)
    oled.show()

# Function to display BPM
def display_bpm(bpm):
    oled.fill(0)
    oled.text("Current BPM:", 0, 0)
    oled.text(str(bpm), 0, 16)
    oled.show()

# Function to start/stop measurement
def toggle_measurement(pin):
    global measuring
    measuring = not measuring
    if measuring:
        print("Measurement started")
        timer.init(period=500, mode=Timer.PERIODIC, callback=update_bpm)
    else:
        print("Measurement stopped")
        timer.deinit()
        display_start_menu()

# Function to update BPM
def update_bpm(timer):
    global bpm, last_beat_time, beat_times
    value = adc.read_u16()
    current_time = time.ticks_ms()

    if value > threshold and (current_time - last_beat_time) > 300:  # Debounce for 300ms
        beat_times.append(current_time)
        last_beat_time = current_time

        if len(beat_times) > 1:
            intervals = [beat_times[i] - beat_times[i - 1] for i in range(1, len(beat_times))]
            avg_interval = sum(intervals) / len(intervals)
            bpm = 60000 / avg_interval  # Convert ms interval to BPM

            if len(beat_times) > 10:  # Keep only the last 10 beat times
                beat_times.pop(0)

    if 40 <= bpm <= 180:  # Ensure realistic BPM values
        display_bpm(int(bpm))
    else:
        print("Invalid BPM value")

# Set up button interrupt
SW0.irq(trigger=Pin.IRQ_FALLING, handler=toggle_measurement)

# Initialize timer
timer = Timer()

# Display the start menu initially
display_start_menu()

# Main loop
while True:
    time.sleep(1)
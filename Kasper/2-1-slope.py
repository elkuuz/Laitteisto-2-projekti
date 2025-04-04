import time
from machine import Pin, I2C # type: ignore
from ssd1306 import SSD1306_I2C # type: ignore
from filefifo import Filefifo # type: ignore

# Constants
SAMPLE_RATE = 250  # Hz
FILE_NAME = 'sample_data/capture_250Hz_01.txt'

# Initialize Filefifo
data = Filefifo(10, name=FILE_NAME)

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

SW0 = Pin(9, Pin.IN, Pin.PULL_UP)
SW1 = Pin(8, Pin.IN, Pin.PULL_UP)
SW2 = Pin(7, Pin.IN, Pin.PULL_UP)

def find_peaks():
    global frequency
    samples = []
    peaks = []
    
    # Read 1000 samples for analysis
    for _ in range(1000):
        samples.append(data.get())
    
    # Find peaks using slope inspection
    for i in range(1, len(samples) - 1):
        if samples[i - 1] < samples[i] > samples[i + 1]:
            peaks.append(i)
    
    # Calculate peak-to-peak intervals
    intervals = [peaks[i] - peaks[i - 1] for i in range(1, len(peaks))]
    intervals_seconds = [interval / SAMPLE_RATE for interval in intervals]
    
    # Print results
    for i in range(min(3, len(intervals))):
        print(f"Interval {i + 1}: {intervals[i]} samples, {intervals_seconds[i]:.3f} seconds")
    
    # Calculate and print frequency
    if intervals:
        avg_interval = sum(intervals) / len(intervals)
        frequency = SAMPLE_RATE / avg_interval
        print(f"Frequency: {frequency:.2f} Hz")
    else:
        print("No peaks found.")
    
    # Display results on OLED
    oled.fill(0)
    oled.text(f"Freq: {frequency:.2f} Hz", 0, 10)
    oled.show()

while True:
    find_peaks()
    time.sleep(1)  # Add a delay to avoid continuous execution
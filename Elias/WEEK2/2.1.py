import array
import math
from machine import I2C, Pin
import ssd1306
import time

class Filefifo:
    def __init__(self, dummy, filename):
        self.filename = filename
        self.data = self._read_file()
        self.index = 0

    def _read_file(self):
        with open(self.filename, 'r') as f:
            return array.array('f', map(float, f.readlines()))

    def read(self, num_samples):
        samples = array.array('f')
        for _ in range(num_samples):
            samples.append(self.data[self.index])
            self.index = (self.index + 1) % len(self.data)
        return samples

# Initialize Filefifo and read data
fifo = Filefifo(10, 'capture_250Hz_01.txt')
sampling_rate = 250  # samples per second
num_samples = 5000  # increase the number of samples to read
signal = fifo.read(num_samples)

# Calculate the slope of the signal
slope = array.array('f', (signal[i+1] - signal[i] for i in range(len(signal) - 1)))

# Identify peaks (where slope changes from positive to negative)
peaks = array.array('i', (i+1 for i in range(len(slope) - 1) if slope[i] > 0 and slope[i+1] < 0))

# Calculate peak-to-peak intervals
peak_to_peak_intervals_samples = array.array('i', (peaks[i+1] - peaks[i] for i in range(len(peaks) - 1)))
peak_to_peak_intervals_seconds = array.array('f', (interval / sampling_rate for interval in peak_to_peak_intervals_samples))

# Calculate the frequency of the signal
average_peak_to_peak_interval_seconds = sum(peak_to_peak_intervals_seconds) / len(peak_to_peak_intervals_seconds)
calculated_frequency = 1 / average_peak_to_peak_interval_seconds

# Initialize I2C and OLED display
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Display results on OLED one by one
for i in range(len(peak_to_peak_intervals_samples)):
    oled.fill(0)
    oled.text("samples:", 0, 0)
    oled.text(str(peak_to_peak_intervals_samples[i]), 0, 10)
    oled.text("seconds:", 0, 20)
    oled.text(str(peak_to_peak_intervals_seconds[i]), 0, 30)
    oled.text("Frequency (Hz):", 0, 40)
    oled.text(str(calculated_frequency), 0, 50)
    oled.show()
    time.sleep(2)  # Display each result for 2 seconds
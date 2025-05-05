from piotimer import Piotimer as Timer  # type: ignore
from ssd1306 import SSD1306_I2C  # type: ignore
from machine import Pin, ADC, I2C, PWM  # type: ignore
from fifo import Fifo  # type: ignore
import utime  # type: ignore
import array
import time
# import network
# import socket
# import urequests as requests
import ujson  # type: ignore

WIFI_SSID = "KMD661_GROUP_MAMUT"
WIFI_PASSWORD = "BlaxicanCocaineSS"

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

SW0 = Pin(9, Pin.IN, Pin.PULL_UP)
SW1 = Pin(8, Pin.IN, Pin.PULL_UP)
SW2 = Pin(7, Pin.IN, Pin.PULL_UP)

ROTA = Pin(10, Pin.IN, Pin.PULL_UP)
ROTB = Pin(11, Pin.IN, Pin.PULL_UP)
ROT_push = Pin(12, Pin.IN, Pin.PULL_UP)

led_onboard = Pin("LED", Pin.OUT)
led21 = PWM(Pin(21))
led21.freq(1000)

adc = ADC(26)

samplerate = 250
samples = Fifo(32)

count = 0
switch_state = 0

avg_size = 128
buffer = array.array('H', [0] * avg_size)


class Menu:
    def __init__(self, options, title="Menu"):
        self.options = options
        self.title = title
        self.selected_index = 0
        self.history_selected_index = 0

    def scroll(self, direction):
        self.selected_index += direction
        if self.selected_index < 0:
            self.selected_index = len(self.options) - 1
        elif self.selected_index >= len(self.options):
            self.selected_index = 0

    def option_select(self, option):
        if option == "MEASURE HR":
            self.measure_hr()
        elif option == "BASIC ANALYSIS":
            self.basic_analysis()
        elif option == "KUBIOS":
            print("Kubios")
        elif option == "HISTORY":
            self.history()

    def display(self):
        oled.fill(0)
        oled.text(">", 0, 20 + self.selected_index * 10)
        oled.text(f"{self.title}", 0, 0)
        for option in range(len(self.options)):
            oled.text(f"{self.options[option]}", 10, 20 + option * 10)

        oled.show()

    def run(self):
        while True:
            if not SW2.value():
                self.scroll(-1)
            if not SW0.value():
                self.scroll(1)
            if not SW1.value():
                pass
            if not ROT_push.value():
                self.option_select(self.options[self.selected_index])
            self.display()
            time.sleep(0.1)

    def history(self):
        oled.fill(0)
        oled.text("History", 32, 20, 1)
        oled.text("loading", 32, 30, 1)
        oled.rect(27, 15, 69, 30, 1)
        oled.show()
        time.sleep(0.5)
        data = History().read_data()
        while True:
            oled.fill(0)
            if data:
                data_length = len(data)
                oled.text("History", 0, 0)
                oled.text(">", 0, 10 + self.history_selected_index * 10)
                for i, line in enumerate(data):
                    oled.text("Measurement " + str(i + 1), 10, 10 + i * 10)

                if not SW0.value():
                    self.history_selected_index += 1
                    if self.history_selected_index >= data_length:
                        self.history_selected_index = 0
                if not SW2.value():
                    self.history_selected_index -= 1
                    if self.history_selected_index < 0:
                        self.history_selected_index = data_length - 1


            else:
                oled.text("No history found", 0, 10)
            oled.show()
            if not ROT_push.value():
                while True:
                    string_data = data[self.history_selected_index]
                    selected_data = eval(string_data)
                    oled.fill(0)
                    oled.text("Selected Data", 0, 0)
                    oled.text("Date:" + str(selected_data["Date"]), 0, 9, 1)
                    oled.text('MeanPPI:' + str(selected_data["MeanPPI"]) + 'ms', 0, 27, 1)
                    oled.text('MeanHR:' + str(selected_data["MeanHR"]) + 'bpm', 0, 18, 1)
                    oled.text('SDNN:' + str(selected_data["SDNN"]) + 'ms', 0, 36, 1)
                    oled.text('RMSSD:' + str(selected_data["RMSSD"]) + 'ms', 0, 45, 1)
                    oled.text('SD1:' + str(selected_data["SD1"]) + ' SD2:' + str(selected_data["SD2"]), 0, 54, 1)
                    print(selected_data)
                    print(time.localtime())
                    oled.show()
                    if not SW1.value():
                        time.sleep(0.1)
                        break
            time.sleep(0.1)
            if not SW1.value():
                break

    def measure_hr(self):
        def measure_hr(self):
            capture_count = 0
            sample_peak = 0
            sample_index = 0
            previous_index = 0
            min_bpm = 30
            max_bpm = 200
            PPI_array = []
            interval_ms = 0

            oled.fill(0)
            oled.text("Measuring HR", 0, 0)
            oled.show()

            # Timer to read ADC data
            tmr = Timer(freq=samplerate, callback=self.read_adc)

            try:
                while True:
                    if not samples.empty():
                        x = samples.get()
                        capture_count += 1

                        # Detect peaks
                        if len(PPI_array) > 0 and x > (sum(PPI_array) / len(PPI_array)) * 1.05:
                            if x > sample_peak:
                                sample_peak = x
                                sample_index = capture_count
                        else:
                            if sample_peak > 0:
                                if (sample_index - previous_index) > (60 * samplerate / min_bpm):
                                    previous_index = sample_index
                                else:
                                    if (sample_index - previous_index) > (60 * samplerate / max_bpm):
                                        interval = sample_index - previous_index
                                        interval_ms = int(interval * 1000 / samplerate)
                                        PPI_array.append(interval_ms)
                                        previous_index = sample_index

                            sample_peak = 0

                        # Calculate and display HR
                        if len(PPI_array) > 1:
                            mean_PPI = self.meanPPI_calculator(PPI_array)
                            actual_HR = self.meanHR_calculator(mean_PPI)
                            oled.fill(0)
                            oled.text(f"HR: {actual_HR} bpm", 0, 0)
                            oled.show()

                    # Exit condition
                    if not SW1.value():
                        break

            finally:
                tmr.deinit()
                oled.fill(0)
                oled.text("Measurement Ended", 0, 0)
                oled.show()

    def meanPPI_calculator(self, data):
        sumPPI = 0
        for i in data:
            sumPPI += i
        rounded_PPI = round(sumPPI / len(data), 0)
        return int(rounded_PPI)

    def meanHR_calculator(self, meanPPI):
        rounded_HR = round(60 * 1000 / meanPPI, 0)
        return int(rounded_HR)

    def SDNN_calculator(self, data, PPI):
        summary = 0
        for i in data:
            summary += (i - PPI) ** 2
        SDNN = (summary / (len(data) - 1)) ** (1 / 2)
        rounded_SDNN = round(SDNN, 0)
        return int(rounded_SDNN)

    def RMSSD_calculator(self, data):
        i = 0
        summary = 0
        while i < len(data) - 1:
            summary += (data[i + 1] - data[i]) ** 2
            i += 1
        rounded_RMSSD = round((summary / (len(data) - 1)) ** (1 / 2), 0)
        return int(rounded_RMSSD)

    def SDSD_calculator(self, data):
        PP_array = array.array('l')
        i = 0
        first_value = 0
        second_value = 0
        while i < len(data) - 1:
            PP_array.append(int(data[i + 1]) - int(data[i]))
            i += 1
        i = 0
        while i < len(PP_array) - 1:
            first_value += float(PP_array[i] ** 2)
            second_value += float(PP_array[i])
            i += 1
        first = first_value / (len(PP_array) - 1)
        second = (second_value / (len(PP_array))) ** 2
        rounded_SDSD = round((first - second) ** (1 / 2), 0)
        return int(rounded_SDSD)

    def SD1_calculator(self, SDSD):
        rounded_SD1 = round(((SDSD ** 2) / 2) ** (1 / 2), 0)
        return int(rounded_SD1)

    def SD2_calculator(self, SDNN, SDSD):
        rounded_SD2 = round(((2 * (SDNN ** 2)) - ((SDSD ** 2) / 2)) ** (1 / 2), 0)
        return int(rounded_SD2)

    def read_adc(self, tid):
        x = adc.read_u16()
        samples.put(x)

    def basic_analysis(self):
        count = 0
        switch_state = 0

        oled.fill(0)
        oled.show()

        x1 = -1
        y1 = 32
        m0 = 65535 / 2
        a = 1 / 10

        disp_div = samplerate / 25
        disp_count = 0
        capture_length = samplerate * 60
        ignore_samples = 5 * samplerate  # Ignore the first 5 seconds of data

        index = 0
        capture_count = 0
        subtract_old_sample = 0
        sample_sum = 0

        min_bpm = 30
        max_bpm = 200
        sample_peak = 0
        sample_index = 0
        previous_peak = 0
        previous_index = 0
        interval_ms = 0
        PPI_array = []

        brightness = 0

        # Bind the read_adc method to the current instance
        tmr = Timer(freq=samplerate, callback=self.read_adc)

        try:
            while capture_count < capture_length:
                if not samples.empty():
                    x = samples.get()
                    capture_count += 1

                    # Skip processing for the first 5 seconds
                    if capture_count <= ignore_samples:
                        continue
                    disp_count += 1

                    if disp_count >= disp_div:
                        disp_count = 0
                        m0 = (1 - a) * m0 + a * x
                        y2 = int(32 * (m0 - x) / 14000 + 35)
                        y2 = max(10, min(53, y2))
                        x2 = x1 + 1
                        oled.fill_rect(0, 0, 128, 9, 1)
                        oled.fill_rect(0, 55, 128, 64, 1)
                        if len(PPI_array) > 3:
                            actual_PPI = self.meanPPI_calculator(PPI_array)
                            actual_HR = self.meanHR_calculator(actual_PPI)
                            oled.text(f'HR:{actual_HR}', 2, 1, 0)
                            oled.text(f'PPI:{interval_ms}', 60, 1, 0)
                        oled.text(
                            f'Timer:  {int(capture_count / samplerate)}s', 18, 56, 0)
                        oled.line(x2, 10, x2, 53, 0)
                        oled.line(x1, y1, x2, y2, 1)
                        oled.show()
                        x1 = x2
                        if x1 > 127:
                            x1 = -1
                        y1 = y2

                    if subtract_old_sample:
                        old_sample = buffer[index]
                    else:
                        old_sample = 0
                    sample_sum = sample_sum + x - old_sample

                    if subtract_old_sample:
                        sample_avg = sample_sum / avg_size
                        sample_val = x
                        if sample_val > (sample_avg * 1.05):
                            if sample_val > sample_peak:
                                sample_peak = sample_val
                                sample_index = capture_count

                        else:
                            if sample_peak > 0:
                                if (sample_index - previous_index) > (60 * samplerate / min_bpm):
                                    previous_peak = 0
                                    previous_index = sample_index
                                else:
                                    if sample_peak >= (previous_peak * 0.8):
                                        if (sample_index - previous_index) > (60 * samplerate / max_bpm):
                                            if previous_peak > 0:
                                                interval = sample_index - previous_index
                                                interval_ms = int(
                                                    interval * 1000 / samplerate)
                                                PPI_array.append(interval_ms)
                                                brightness = 5
                                                led21.duty_u16(4000)
                                            previous_peak = sample_peak
                                            previous_index = sample_index
                            sample_peak = 0

                        if brightness > 0:
                            brightness -= 1
                        else:
                            led21.duty_u16(0)

                    buffer[index] = x
                    index += 1
                    if index >= avg_size:
                        index = 0
                        subtract_old_sample = 1

                # Check if the rotary encoder button is pressed
                if not SW1.value():
                    oled.fill(0)
                    oled.text("Analysis Cancelled", 0, 0)
                    oled.show()
                    time.sleep(1)
                    time.sleep(0.5)  # Debounce delay
                    break

        finally:
            tmr.deinit()

            while not samples.empty():
                x = samples.get()

            oled.fill(0)
            oled.text("Returning to Menu", 0, 0)
            oled.show()
            time.sleep(1)


class History:
    def save_data(self, data):
        with open('sample_history.txt', 'a') as f:
            f.write(data + "\n")

    def read_data(self):
        try:
            with open('sample_history.txt', 'r') as f:
                data = f.readlines()
            return data

        except:
            print("no file :(")
            return

    def delete_data(self):
        with open('sample_history.txt', 'w') as f:
            f.write("")
        return "History cleared"


class Kubios:
    def __init__(self):
        pass

    def run(self):
        pass


menu = Menu(["MEASURE HR", "BASIC ANALYSIS",
             "KUBIOS", "HISTORY"], "Beat Buddy")

menu.run()

from piotimer import Piotimer as Timer  # type: ignore
from ssd1306 import SSD1306_I2C  # type: ignore
from machine import Pin, ADC, I2C, PWM  # type: ignore
from fifo import Fifo  # type: ignore
import array, time, network, ujson, ntptime  # type: ignore
from umqtt.simple import MQTTClient  # type: ignore

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

avg_size = 128
buffer = array.array('H', [0]*avg_size)


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
        analysis = Analysis()
        if option == "MEASURE HR":
            analysis.measure_hr()
        elif option == "BASIC ANALYSIS":
            analysis.basic_analysis()
        elif option == "KUBIOS":
            Kubios().run()
        elif option == "HISTORY":
            self.history()

    def display(self):
        oled.fill(0)
        oled.text(">", 0, 20 + self.selected_index * 10)
        oled.fill_rect(0, 0, 128, 15, 1)

        oled.text(f"{self.title}", 4, 4, 0)
        for option in range(len(self.options)):
            oled.text(f"{self.options[option]}", 10, 20 + option * 10)

        oled.show()

    def run(self):
        self.start_phase()
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

    def start_phase(self):
        oled.fill(0)
        oled.text("Beat Buddy 3000", 0, 15, 1)
        oled.text("Starting up", 0, 30, 1)
        oled.show()
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        breakpoint = 0
        # Attempt to connect once per half second for 5 seconds
        while wlan.isconnected() == False:
            print("Connecting... ")
            time.sleep(0.5)
            breakpoint += 1
            if breakpoint >= 10:
                oled.fill(0)
                oled.text("No internet", 0, 15, 1)
                oled.text("Kubios analysis", 0, 30, 1)
                oled.text("not available", 0, 40, 1)
                oled.show()
                time.sleep(2)
                break
        if wlan.isconnected():
            if time.localtime()[0] < 2025:
                ntptime.settime()

        return

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
                if data_length > 5:
                    History().delete_first_data()
                    data = History().read_data()
                oled.text("History", 0, 0)
                oled.text(">", 0, 10 + self.history_selected_index * 10)
                for i, line in enumerate(data):
                    oled.text(str(eval(line)["Date"]), 10, 10 + i * 10)

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
                    oled.text(str(selected_data["Date"]), 0, 9, 1)
                    oled.text(
                        'MeanPPI:' + str(selected_data["MeanPPI"]) + 'ms', 0, 27, 1)
                    oled.text(
                        'MeanHR:' + str(selected_data["MeanHR"]) + 'bpm', 0, 18, 1)
                    oled.text(
                        'SDNN:'+str(selected_data["SDNN"]) + 'ms', 0, 36, 1)
                    oled.text(
                        'RMSSD:'+str(selected_data["RMSSD"]) + 'ms', 0, 45, 1)
                    oled.show()
                    if not SW1.value():
                        time.sleep(0.1)
                        break
            time.sleep(0.1)
            if not SW1.value():
                break


class Analysis:
    def __init__(self):
        self.min_bpm = 30
        self.max_bpm = 200

    def meanPPI_calculator(self, data):
        if not data:  # Handle empty list
            return 0
        return int(round(sum(data) / len(data), 0))

    def meanHR_calculator(self, meanPPI):
        if meanPPI <= 0:  # Avoid division by zero
            return 0
        hr = 60_000 / meanPPI
        return int(round(hr, 0))

    def current_HR_calculator(self, PPI_array):
        if len(PPI_array) < 1:
            return 0
        latest_PPI = PPI_array[-1]  # Use the most recent PPI
        return int(round(60_000 / latest_PPI, 0))

    def SDNN_calculator(self, data, PPI):
        summary = 0
        for i in data:
            summary += (i-PPI)**2
        SDNN = (summary/(len(data)-1))**(1/2)
        rounded_SDNN = round(SDNN, 0)
        return int(rounded_SDNN)

    def RMSSD_calculator(self, data):
        i = 0
        summary = 0
        while i < len(data)-1:
            summary += (data[i+1]-data[i])**2
            i += 1
        rounded_RMSSD = round((summary/(len(data)-1))**(1/2), 0)
        return int(rounded_RMSSD)

    def read_adc(self, tid):
        x= adc.read_u16()
        if x > 0:
            samples.put(x)

    def measure_hr(self):
        oled.fill(0)
        oled.text("Place finger", 0, 0)
        oled.text("on sensor", 0, 10)
        oled.show()

        # Signal processing variables
        sample_sum = index = subtract_old_sample = 0
        sample_peak = 0
        sample_index = 0
        previous_peak = 0
        previous_index = 0
        PPI_array = []
        buffer = [0] * avg_size  # Make sure avg_size is defined

        x1 = -1
        y1 = 32
        m0 = 32768
        a = 0.1
        # Ignore first 5 seconds for stabilization
        ignore_samples = 5 * samplerate
        capture_count = 0

        tmr = Timer(freq=samplerate, callback=self.read_adc)

        try:
            while True:
                if not samples.empty():
                    sample_val = samples.get()
                    capture_count += 1

                    # Skip initial unstable period
                    if capture_count <= ignore_samples:
                        continue

                    # Update display every 100ms
                    if capture_count % (samplerate//10) == 0:
                        m0 = (1 - a) * m0 + a * sample_val
                        y2 = max(
                            10, min(53, int(32 * (m0 - sample_val) * (1/14000) + 35)))
                        x2 = x1 + 1
                        oled.fill_rect(0, 0, 128, 9, 1)
                        oled.fill_rect(0, 55, 128, 64, 1)
                        if len(PPI_array) >= 1:  # Need at least 1 interval for HR
                            current_hr = int(60000 / (sum(PPI_array[-3:])/len(PPI_array[-3:]))) if len(PPI_array) >= 3 else int(60000/PPI_array[-1])
                            oled.text(f'HR: {current_hr}', 2, 1, 0)
                            print(f"HR: {current_hr} (PPI: {PPI_array[-1]}ms)")  # Debug
                        else:
                            oled.text("HR: --", 2, 1, 0)
                        oled.line(x2, 10, x2, 53, 0)
                        oled.line(x1, y1, x2, y2, 1)
                        oled.text("SW1 to exit", 2, 56, 0)
                        oled.show()
                        x1 = x2 if x2 <= 127 else -1
                        y1 = y2

                    # Signal processing - moving average
                    if subtract_old_sample:
                        old_sample = buffer[index]
                    else:
                        old_sample = 0
                    sample_sum += sample_val - old_sample

                    if subtract_old_sample:
                        sample_avg = sample_sum / avg_size
                        
                        # Simple peak detection (when value crosses 10% above average)
                        if sample_val > sample_avg * 1.10:
                            if sample_val > sample_peak:
                                sample_peak, sample_index = sample_val, capture_count
                        else:
                            if sample_peak > 0:  # We had a peak
                                if previous_peak > 0:  # Not the first peak
                                    interval_ms = int((sample_index - previous_index) * 1000 / samplerate)
                                    # Only keep reasonable intervals (40-180 bpm)
                                    if 333 < interval_ms < 1500:  # 40-180 bpm
                                        PPI_array.append(interval_ms)
                                        # Keep only last 5 intervals
                                        if len(PPI_array) > 5:
                                            PPI_array = PPI_array[-5:]
                                        led21.duty_u16(4000)  # Flash LED on pulse
                                        time.sleep_ms(50)
                                        led21.duty_u16(0)
                                        
                                previous_peak, previous_index = sample_peak, sample_index
                                sample_peak = 0

                    buffer[index] = sample_val
                    index = (index + 1) % avg_size
                    if index == 0:
                        subtract_old_sample = 1

                # Exit condition
                if not SW1.value():
                    oled.fill(0)
                    oled.text("Exiting HR", 0, 0)
                    oled.show()
                    time.sleep(1)
                    break

        finally:
            tmr.deinit()
            while not samples.empty():
                samples.get()
            led21.duty_u16(0)
    def basic_analysis(self, kubios=False):

        oled.fill(0)
        oled.show()

        x1 = -1
        y1 = 32
        m0 = 32768
        a = 0.1

        disp_div = samplerate / 25
        disp_count = 0
        capture_length = samplerate * 35
        ignore_samples = 5 * samplerate  # Ignore the first 5 seconds of data

        capture_count = 0
        sample_sum = index = subtract_old_sample = 0

        sample_peak = 0
        sample_index = 0
        previous_peak = 0
        previous_index = 0
        interval_ms = 0
        PPI_array = []

        brightness = 0
        oled.fill(0)
        oled.text("Place finger", 0, 0)
        oled.text("on sensor", 0, 10)
        oled.show()

        # Bind the read_adc method to the current instance
        tmr = Timer(freq=samplerate, callback=self.read_adc)

        try:
            while capture_count < capture_length:
                if not samples.empty():
                    sample_val = samples.get()
                    capture_count += 1

                    # Skip processing for the first 5 seconds
                    if capture_count <= ignore_samples:
                        continue
                    disp_count += 1

                    if disp_count >= disp_div:
                        disp_count = 0
                        m0 = (1 - a) * m0 + a * sample_val
                        y2 = max(
                            10, min(53, int(32 * (m0 - sample_val) * (1/14000) + 35)))
                        x2 = x1 + 1
                        oled.fill_rect(0, 0, 128, 9, 1)
                        oled.fill_rect(0, 55, 128, 64, 1)
                        if len(PPI_array) > 3 and not kubios:
                            mean_PPI = self.meanPPI_calculator(PPI_array)
                            mean_HR = self.meanHR_calculator(mean_PPI)
                            current_HR = self.current_HR_calculator(PPI_array)
                            oled.text(f'HR:{current_HR}', 2, 1, 0)
                            oled.text(f'PPI:{interval_ms}', 60, 1, 0)
                        elif kubios:
                            oled.text('Gathering data', 2, 1, 0)
                        oled.text(
                            f'Timer:  {int(capture_count / samplerate) - 5}s', 18, 56, 0)
                        oled.line(x2, 10, x2, 53, 0)
                        oled.line(x1, y1, x2, y2, 1)
                        oled.show()
                        x1 = x2 if x2 <= 127 else -1
                        y1 = y2

                    if subtract_old_sample:
                        old_sample = buffer[index]
                    else:
                        old_sample = 0
                    sample_sum += sample_val - old_sample

                    if subtract_old_sample:
                        sample_avg = sample_sum / avg_size
                        if sample_val > (sample_avg * 1.05):
                            if sample_val > sample_peak:
                                sample_peak, sample_index = sample_val, capture_count

                        else:
                            if sample_peak > 0:
                                if (sample_index - previous_index) > (60 * samplerate / self.min_bpm):
                                    previous_peak = 0
                                    previous_index = sample_index
                                else:
                                    if sample_peak >= (previous_peak * 0.8):
                                        if (sample_index - previous_index) > (60 * samplerate / self.max_bpm):
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

                    buffer[index] = sample_val
                    index += 1
                    if index >= avg_size:
                        index = 0
                        subtract_old_sample = 1

                # Check if the rotary encoder button is pressed
                if not SW1.value():
                    oled.fill(0)
                    oled.text("Analysis ", 0, 0)
                    oled.text("Cancelled", 0, 10)
                    oled.show()
                    time.sleep(1)
                    time.sleep(0.5)  # Debounce delay
                    break

        finally:
            tmr.deinit()

        while not samples.empty():
            sample_val = samples.get()

        if len(PPI_array) > 1 and not kubios:
            # Calculate the statistics
            mean_PPI = self.meanPPI_calculator(PPI_array)
            mean_HR = self.meanHR_calculator(mean_PPI)
            SDNN = self.SDNN_calculator(PPI_array, mean_PPI)
            RMSSD = self.RMSSD_calculator(PPI_array)

            # Display the calculated stats
            oled.fill(0)
            oled.text(f"Mean HR: {mean_HR} bpm", 0, 10)
            oled.text(f"Mean PPI: {mean_PPI} ms", 0, 20)
            oled.text(f"SDNN: {SDNN} ms", 0, 30)
            oled.text(f"RMSSD: {RMSSD} ms", 0, 40)
            oled.text("SW1 to go back", 0, 50)
            oled.show()

            year = time.localtime()[0]
            month = time.localtime()[1]
            day = time.localtime()[2]
            hour = time.localtime()[3] + 3
            minute_fake = time.localtime()[4]
            minute_real = f"{minute_fake:02d}"
            data_dict = {
                "Date": str(hour) + ":" + str(minute_real) + " " + str(day) + "." + str(month) + "." + str(year),
                "MeanPPI": int(mean_PPI),
                "MeanHR": int(mean_HR),
                "SDNN": int(SDNN),
                "RMSSD": int(RMSSD),
            }
            History().save_data(
                f'{data_dict}')
        elif kubios:
            kubios_data = {"id": 420, "type": "PPI", "data": PPI_array, "analysis": {"type": "readiness"}}
            kubios_data_json = ujson.dumps(kubios_data)
            print(kubios_data_json)
            return kubios_data_json
        else:
            # Display a message if insufficient data
            oled.fill(0)
            oled.text("Insufficient Data", 0, 0)
            oled.text("Try Again", 0, 10)
            oled.show()

        # Wait for exit
        while SW1.value():
            pass
        time.sleep(0.5)  # Debounce


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

    def delete_first_data(self):
        with open('sample_history.txt', 'r') as f:
            lines = f.readlines()
        with open('sample_history.txt', 'w') as f:
            for line in lines[1:]:
                f.write(line)
        return "First line deleted"


class Kubios:
    def __init__(self):
        self.mqtt_client = None
        self.kubios_response = None
        self.wlan = None
        
    def connect_to_mqtt(self):
        try:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            self.mqtt_client = MQTTClient("KubiosClient", "192.168.8.253", 21883)
            self.mqtt_client.connect()
            self.mqtt_client.set_callback(self.kubios_response_callback)
            self.mqtt_client.subscribe("kubios-response")
            print("Connected to MQTT successfully")
        except Exception as e:
            print(f"Failed to connect to MQTT: {e}")
    
    def kubios_response_callback(self, topic, msg):
        try:
            self.kubios_response = ujson.loads(msg)
            print(f"Received response: {self.kubios_response}")
        except Exception as e:
            print(f"Failed to parse response: {e}")

    def test_connection(self):
        print("Testing Kubios connection...")
        if self.wlan.status() != 3:
            print("WiFi is not connected!")
            return False
            
        kubios_data = Analysis().basic_analysis(kubios=True)
        self.mqtt_client.publish("kubios-request", kubios_data)
        print("Sent test message")
        
        for attempt in range(4):
            time.sleep(0.5)
            self.mqtt_client.check_msg()
            if self.kubios_response and self.kubios_response.get("id") == 420:
                print("Kubios connection is working")
                return True
                
        print("No valid response from Kubios")
        return False
        
    def send_data(self, data):
        try:
            message = ujson.dumps(data)
            self.mqtt_client.publish("kubios-request", message)
            print("Data sent to Kubios successfully")
        except Exception as e:
            print(f"Failed to send data: {e}")

    def loading_screen(self):
        oled.fill(0)
        oled.text("Loading", 0, 0)
        oled.show()
        time.sleep(0.2)
    def run(self):
        self.loading_screen()
        self.connect_to_mqtt()
        if self.test_connection():
            self.show_output(self.kubios_response)
            pass
        else:
            oled.fill(0)
            oled.text("Kubios", 0, 0)
            oled.text("Connection", 0, 10)
            oled.text("Failed", 0, 20)
            oled.show()
            time.sleep(2)
            return
    def show_output(self, data):
        try:
            # Safely extract data with error checking
            analysis = data.get("data", {}).get("analysis", {})
            
            # Round values with fallback in case of missing data
            kubios_mean_hr = round(analysis.get("mean_hr_bpm", 0), 0)
            kubios_mean_ppi = round(analysis.get("mean_rr_ms", 0), 0)
            kubios_sdnn = round(analysis.get("sdnn_ms", 0), 0)
            kubios_rmssd = round(analysis.get("rmssd_ms", 0), 0)
            kubios_sns = round(analysis.get("sns_index", 0), 3)
            kubios_pns = round(analysis.get("pns_index", 0), 3)
            
            # Clear display
            oled.fill(0)
            
            # Display rounded values
            oled.text(f"Mean HR: {int(kubios_mean_hr)}bpm", 0, 0)
            oled.text(f"Mean PPI: {int(kubios_mean_ppi)}ms", 0, 10)
            oled.text(f"SDNN: {int(kubios_sdnn)}ms", 0, 20)
            oled.text(f"RMSSD: {int(kubios_rmssd)}ms", 0, 30)
            oled.text(f"SNS: {kubios_sns:.3f}", 0, 40)  # Keep 3 decimal places
            oled.text(f"PNS: {kubios_pns:.3f}", 0, 50)  # Keep 3 decimal places
            
            oled.show()
            
            # Wait for button press (with debounce)
            while True:
                if not SW1.value():
                    time.sleep(0.5)  # Debounce delay
                    break
                time.sleep(0.1)
                
        except Exception as e:
            print(f"[ERROR] Failed to display output: {e}")
            oled.fill(0)
            oled.text("Display Error", 0, 0)
            oled.text("Check Data", 0, 20)
            oled.show()
        
            

menu = Menu(["MEASURE HR", "BASIC ANALYSIS",
            "KUBIOS", "HISTORY"], "Beat Buddy 3000")

menu.run()

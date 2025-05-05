from machine import Pin, ADC
import time

adc = ADC(26)  # ADC0 on GP26

while True:
    adc_count = adc.read_u16()  # Read raw ADC count (0-65535)
    voltage = adc_count * (3.3 / 65535)  # Convert ADC reading to voltage

    # Determine digital state based on voltage
    if voltage >= 2.0:
        digital_state = 1
    elif voltage <= 0.8:
        digital_state = 0
    else:
        digital_state = None  # Forbidden zone

    # Print ADC count, voltage, and digital state
    print(f"ADC Count: {adc_count} | Voltage: {voltage:.2f}V | Digital State: {digital_state}")

    if digital_state == 1:
        print("--> HIGH detected!")
    elif digital_state == 0:
        print("--> LOW detected!")
    else:
        print("--> Forbidden zone!")

    time.sleep(0.5)  # Slow down readings
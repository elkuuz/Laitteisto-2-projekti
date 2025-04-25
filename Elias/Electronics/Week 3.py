from machine import Pin, ADC
import utime

# Pin configuration
adc_pin = ADC(26)  # ADC pin (GP26)
digital_pin = Pin(15, Pin.IN)  # Digital input pin (GP15)

# Variables to track state
last_state = digital_pin.value()

print("Monitoring digital pin and ADC voltage...")

while True:
    current_state = digital_pin.value()

    # Detect state change
    if current_state != last_state:
        # Read ADC voltage
        adc_value = adc_pin.read_u16()  # ADC value (0-65535)
        voltage = adc_value * 3.3 / 65535  # Convert to voltage (3.3V reference)

        # Print the state change and corresponding voltage
        if current_state == 1:
            print(f"State changed to HIGH. Voltage: {voltage:.2f} V")
        else:
            print(f"State changed to LOW. Voltage: {voltage:.2f} V")

        # Update last state
        last_state = current_state

    # Small delay to avoid excessive CPU usage
    utime.sleep(0.01)
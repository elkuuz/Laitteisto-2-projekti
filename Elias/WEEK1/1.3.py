import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# Initialize the OLED display
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize buttons
button_up = Pin(9, Pin.IN, Pin.PULL_UP)    # SW0
button_clear = Pin(8, Pin.IN, Pin.PULL_UP) # SW1
button_down = Pin(7, Pin.IN, Pin.PULL_UP)  # SW2

# Initialize variables
x = 0
y = oled_height // 2
speed = 1

# Clear the display
oled.fill(0)
oled.show()

while True:
    # Clear the screen and reset position if SW1 is pressed
    if button_clear.value() == 0:
        oled.fill(0)
        x = 0
        y = oled_height // 2
        oled.show()
        time.sleep(0.2)  # Debounce delay

    # Move the pixel up if SW0 is pressed
    if button_up.value() == 0:
        y = max(0, y - 1)
        time.sleep(0.05)  # Debounce delay

    # Move the pixel down if SW2 is pressed
    if button_down.value() == 0:
        y = min(oled_height - 1, y + 1)
        time.sleep(0.05)  # Debounce delay

    # Draw the pixel
    oled.pixel(x, y, 1)
    oled.show()

    # Move to the next position
    x += speed
    if x >= oled_width:
        x = 0

    # Small delay to control drawing speed
    time.sleep(0.01)
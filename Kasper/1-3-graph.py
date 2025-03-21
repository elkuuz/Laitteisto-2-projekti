import time
from machine import Pin, I2C # type: ignore
from ssd1306 import SSD1306_I2C # type: ignore

# Initialize OLED display
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize buttons
SW0 = Pin(9, Pin.IN, Pin.PULL_UP)  # Move up
SW1 = Pin(8, Pin.IN, Pin.PULL_UP)  # Clear screen
SW2 = Pin(7, Pin.IN, Pin.PULL_UP)  # Move down

# Constants
middle_y = oled_height // 2  # Start drawing from the middle of the screen
x = 0  # Start drawing from the left side
y = middle_y  # Current y-coordinate

# Clear the screen
oled.fill(0)
oled.show()

while True:
    # Check button states
    if not SW2.value():  # SW0 pressed (move up)
        y = max(0, y - 1)  # Ensure y doesn't go above the screen
    if not SW0.value():  # SW2 pressed (move down)
        y = min(oled_height - 1, y + 1)  # Ensure y doesn't go below the screen
    if not SW1.value():  # SW1 pressed (clear screen)
        oled.fill(0)  # Clear the screen
        x = 0  # Reset x to the left side
        y = middle_y  # Reset y to the middle of the screen

    # Draw the pixel at the current position
    oled.pixel(x, y, 1)
    oled.show()

    # Move to the next x-coordinate
    x += 1
    if x >= oled_width:  # If we reach the right edge, wrap back to the left
        x = 0

    # Small delay to control drawing speed
    time.sleep(0.01)
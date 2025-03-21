import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

SW0 = Pin(9, Pin.IN, Pin.PULL_UP)
SW1 = Pin(8, Pin.IN, Pin.PULL_UP)
SW2 = Pin(7, Pin.IN, Pin.PULL_UP)

# Initialize OLED display
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Clear the display
oled.fill(0)
oled.show()

# Constants
line_height = 10  # Height of each line in pixels
max_lines = oled_height // line_height  # Maximum number of lines on the screen
lines = []  # List to store lines of text

print("Type your input below:")

while True:
    # Read user input from the keyboard
    user_input = input("> ")

    # Add the new input to the list of lines
    lines.append(user_input)

    # If the screen is full, remove the top line to make room for new text
    if len(lines) > max_lines:
        lines.pop(0)

    # Clear the display
    oled.fill(0)

    # Draw each line on the OLED screen
    for i, line in enumerate(lines):
        oled.text(line, 0, i * line_height)

    # Update the display
    oled.show()
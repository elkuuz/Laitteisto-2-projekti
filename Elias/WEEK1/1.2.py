import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# Initialize the OLED display
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Clear the display
oled.fill(0)
oled.show()

# Initialize variables
line_height = 10
max_lines = oled_height // line_height
lines = []

while True:
    # Read user input from the keyboard
    user_input = input("Enter text: ")

    # Add the new input to the list of lines
    lines.append(user_input)

    # If the number of lines exceeds the maximum, remove the oldest line
    if len(lines) > max_lines:
        lines.pop(0)

    # Clear the display
    oled.fill(0)

    # Draw each line on the display
    for i, line in enumerate(lines):
        oled.text(line, 0, i * line_height)

    # Update the display
    oled.show()
# MicroPython libraries for the first year hardware project

This is an example project that can be used to install MicroPython libraries that are needed for
the first year hardware project. You can also use this as a template for your own 
project.

# To setup your Pico

You need to have git installed. Make sure that you have python installed and that is in the path. You can verify this in terminal
by running <kbd>python --version</kbd> or <kbd>python3 --version</kbd>. If you see python version then python is in the path.

You also need to have mpremote installed. To install mpremote:

- <kbd>pip install mpremote</kbd>
  
  or
  
- <kbd>python -m pip install mpremote</kbd>

When the prerequisites are met then you can install the project and the libraries to your Pico.

## Check out the repository and install libraries

Start a terminal, go to (use <kbd>cd</kbd> command) the directory where you want to copy the project to. Then run:

<kbd>git clone --recurse-submodules https://gitlab.metropolia.fi/lansk/pico-test.git</kbd>

Go to the pico-test directory and run:

- <kbd>.\install.cmd</kbd> if you use Windows PowerShell or cmd

- <kbd>./install.sh</kbd> if you use Linux, OSX or GitBash

## Pull submodule updates

When a submodule is added a commit id is stored to the repository where the module is set up. 
If the submodule is updated the updates aren't automatically applied to the repository. To get the
updates run:

<kbd>git submodule update --recursive --remote</kbd>

After this command you have the latest commit in your local copy of the submodule. 
Note that if you do <kbd>git diff</kbd> right after update you see only one changed
line. The line shows that submodule commit id has changed. 
To apply the changes to your remote you must add the changed submodule 
with <kbd>git add</kbd> and commit. After the commit you will see a different
commit id next to the submodule when you view the remote repository in the browser.


# Laitteisto-2-projekti

## I will kys


## shit to not forgor
```python 
import time 
from machine import UART, Pin, I2C, Timer, ADC  # type: ignore
from ssd1306 import SSD1306_I2C  # type: ignore

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
```

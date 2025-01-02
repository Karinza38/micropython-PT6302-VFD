"""
  test_prox_digit.py test example for the PT6302 VFD Driver.

  Display digits and values on the top part of the LCD.

  - Focus: Manipulate the digits
  - VFD Model: Proximus TV/Belgacom TV  Vaccum Fluorescent Display

The MIT License (MIT)
Copyright (c) 2024 Dominique Meurisse, support@mchobby.be, shop.mchobby.be

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from vfd_proximus import *
from machine import Pin
import time

d = VFD_Proximus( sck_pin=Pin.board.GP16, sdata_pin=Pin.board.GP13, cs_pin=Pin.board.GP14, reset_pin=Pin.board.GP18 )
d.print("VFD Proximus") # Can add a position from 1 to 12 in second position!

# ---- Working with SINGLE DIGIT ------------------------------------

# From left to right digits
d.center.set_digit( 0, 6 ) # Digit 0 = 6
d.center.set_digit( 1, 7 ) # Digit 0 = 7
d.center.set_digit( 2, 8 ) # Digit 0 = 8
d.center.set_digit( 3, 9 ) # Digit 0 = 9
d.center.set_digit( 4, 1 ) # Digit 4 = can only be 1 or Nothing
d.center.update() # Refresh the display
d.center.separator = COLON
d.center.update() # Refresh the display
time.sleep(2)
d.center.separator = DOT
d.center.update() # Refresh the display
time.sleep(2)
d.center.separator = None
d.center.update() # Refresh the display
time.sleep(2)

d.left.set_digit( 0, 1 )
d.left.set_digit( 1, 2 )
d.left.set_digit( 2, None ) # Set it off
d.left.set_digit( 3, 4 )
d.left.set_digit( 4, None ) # Set it off
d.left.update() # Refresh the display

# ---- Working with INTEGER ---------------------------------------

# Directly update the value on the left AND part of the display.
left_value = 199
right_value = 99
while True:
  d.center.set( digit_group2=left_value, digit_group1=right_value)
  d.center.update()
  time.sleep_ms( 50 )
  # Decrement counters
  left_value -= 1
  right_value -= 1
  if right_value < 0:
    right_value = 0
  if left_value == 0:
    break # stop the lopp

# Clear the both groups of digits
d.left.clear( digit_group_index=1 )
d.left.clear( digit_group_index=2 )
# Clear the both groups of digits
d.center.clear( digit_group_index=1 )
d.center.clear( digit_group_index=2 )
d.update()


# Update the right Panel
for i in range( 100 ): # 0..99
  d.right.set( i )
  d.right.separator = COLON if i%2==1 else None
  d.right.update()
  time.sleep_ms( 50 )

# Clear the digits
d.right.clear()
d.update()
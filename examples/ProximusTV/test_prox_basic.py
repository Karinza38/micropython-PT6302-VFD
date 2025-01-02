"""
  test_prox_basic.py test example for the PT6302 VFD Driver.

	demonstrate the main functions for Proximus display

  - Focus: Showing text and light-up symbol.
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
# Print & options are the ONLY COMMANDS NOT REQUIRING update() call to refresh the screen
d.print("VFD Proximus") # Can add a position from 1 to 12 in second position!

# Light up all options (one by one)
#   TITLE, CHANNEL, TRACK, STEREO, RECORD, CLOCK, ANTENNA, AM, FM
for option in ALL_OPTIONS:
	d.options += option
	time.sleep_ms( 500 )
# Light off all options (one by one)
for option in ALL_OPTIONS:
	d.options -= option
	time.sleep_ms( 500 )

d.clrscr()
d.print("Done !")
"""
  test_btn_segment.py test example for the PT6302 VFD Driver.

    Wire GP0 to ground via a button, GP1 to ground via a button
    Pressing the buttons will decrease or increase the segment number.
    Segment number is displayed in REPL and onto the display (from position 0)

  - Focus: Press BTN GP0 to decrease 
           When a given digit is wired to symbols, this example will be great 
           to discover which symbol is linked to a given segment.

  - VFD Model: all

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

from machine import Pin
from vfd_pt63 import VFD_PT6302, DigitSegments, RAM7
import time

VFD_DIGIT = 2  # Digit to be tested. Index from 1..16. 

# --- button interface --------------------------------------
last_ms = time.ticks_ms()
segment_idx = 0

def cb_less(pin):
	global last_ms, segment_idx
	_now =  time.ticks_ms()
	if time.ticks_diff( _now, last_ms )>300:
		if segment_idx>0:
			segment_idx -= 1
		last_ms = _now

def cb_more(pin):
	global last_ms, segment_idx
	_now =  time.ticks_ms()
	if time.ticks_diff( _now, last_ms )>300:
		if segment_idx<34:
			segment_idx += 1
		last_ms = _now


# Setup the button input pin with a pull-up resistor.
btn_less = Pin( Pin.board.GP0 , Pin.IN, Pin.PULL_UP)
btn_more = Pin( Pin.board.GP1 , Pin.IN, Pin.PULL_UP)
# Register an interrupt on rising button input.
btn_less.irq(cb_less, Pin.IRQ_RISING)
btn_more.irq(cb_more, Pin.IRQ_RISING)

# --- display interface -------------------------------------

_reset = Pin(Pin.board.GP18, Pin.OUT, value=True ) # Unactive
_cs = Pin( Pin.board.GP14, Pin.OUT, value=True ) # unactiva
_sdata = Pin( Pin.board.GP13, Pin.OUT )
_sck = Pin( Pin.board.GP16, Pin.OUT, value=True )

vfd =VFD_PT6302( sck=_sck, sdata=_sdata, cs=_cs, reset=_reset, digits=15 )

# Attach a digit to custom char. Allow to control symbols
segments = vfd.attach_digit( VFD_DIGIT, RAM7 ) 

last_segment_idx = None
while True:
	# Did the segment value changed ?
	if last_segment_idx != segment_idx:
		s = "D %2i Seg %2i" % (VFD_DIGIT, segment_idx )
		# Display on REPL
		print( s )
		# Display on VFD 
		vfd.display_digit(4, s) # print for position 1 with auto_increment
		# Update the segment
		segments.clear()
		segments.set(segment_idx, True )
		segments.update()
		# Remember
		last_segment_idx = segment_idx 
	time.sleep_ms(100)
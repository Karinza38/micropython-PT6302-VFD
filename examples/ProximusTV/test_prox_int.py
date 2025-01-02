"""
  test_prox_float.py test example for the PT6302 VFD Driver.

  - Focus: Showing float value on a panel.
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
d.print("Show Integer") # Can add a position from 1 to 12 in second position!


VALUES =  [65,197,2197,13477,1782,347,32]

for value in VALUES:
	d.center.int( value )
	d.update()
	time.sleep(1)
d.center.clear()


for value in VALUES:
	d.left.int( value )
	d.update()
	time.sleep(1)
d.left.clear()

d.clrscr()
d.print('Done!')



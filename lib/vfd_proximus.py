
"""
  vfd_proximus.py is a micropython module for PT6302 VFD driver (Vaccum Fluorescent Display)
          used in the Proximux TV / Belgacom TV version 4. It helps to control the various symbols.



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
from vfd_pt63 import *
from micropython import const
import time

TITLE = const(1)
CHANNEL = const(2)
TRACK = const(3)
STEREO = const(4)
RECORD = const(5)
CLOCK = const(6)
ANTENNA = const(7)
AM = const(8)
FM = const(9)

ALL_OPTIONS = set( [TITLE,CHANNEL,TRACK,STEREO,RECORD,CLOCK,ANTENNA,AM,FM] )

# Separator value
COLON = const(2)
DOT = const(1)

class OptionSet( set ):
	def __init__( self, owner, values ):
		super().__init__( values )
		self.owner = owner # The VFD_Proximus instance

	def __iadd__( self, other ):
		assert type(other) is int
		self.update( [other] )
		self.owner.update()
		return self

	def __isub__( self, this ):
		assert type(this) is int
		self.remove( this )
		self.owner.update()
		return self


class BasePanel():
	# for 0,1,..9, status for ...,seg2,seg1,seg0 
	DIGITS = [ 0b01110111, 0b00010010, 0b01011101, 0b01011011, 0b00111010, 0b01101011, 0b01101111, 0b01010010, 0b01111111, 0b01111011 ] 
	
	def __init__( self, owner, segments ):
		self.owner = owner
		self._seg = segments
		self._root = None # Must be defined in descendant
		self._point = None 

	def set_digit( self, digit_num, value ):
		""" Initialize the segments of a given digit 0..4 (0 is the right most) """
		assert (value==None) or (0<=value<=9)
		assert 0<=digit_num<=4

		# Digit 4 is for hundred --> only on segment to light!
		if digit_num==4:
			self._seg.set( self._root[digit_num], (value != None) and (value > 0) )
		else:
			bits = self.DIGITS[value] if value!=None else 0b00000000
			for segment_idx in range( 7 ):
				mask = (1 << segment_idx)
				#print( "segment", self._root[digit_num]+segment_idx, "value", (bits & mask) == mask )
				self._seg.set( self._root[digit_num]+segment_idx, (bits & mask) == mask)

	@property
	def separator( self ):
		""" Hide or Show any separator (1,2 or None)"""
		return self._sep 

	@separator.setter
	def separator( self, value ):
		self._seg.set( self._point, value in (COLON,) )
		self._seg.set( self._point+1, value in (COLON,DOT) )
		self._sep = value


	def decompose( self, value ):
		# Decompose a value in digits
		_s = str(value)
		digits = [ int(_s[i]) for i in range( len(_s)-1,-1,-1 )]
		units = digits[0]
		tens  = 0
		if len(digits)>1:
			tens = digits[1]
		hundreds = 0
		if len(digits)>2:
			hundreds = digits[2]
		return( units, tens, hundreds )


	def update( self ):
		""" Sending the data to the VFD """
		self._seg.update()



class DigitalPanel( BasePanel ):
	def __init__( self, owner, segments ):
		super().__init__( owner, segments )
		self._root = [0,8,17,25,33] # Root of each number (1rst segment of each digit, from left to right)
		self._point = 15 # (on top) and 16 (on the bottom)

	def set( self, digit_group2=None, digit_group1=None ):
		""" Allows to set the digits segments. Group 1 is on the right, group 2 on the left """
		#assert (digit_group1!=None) and (00 <= digit_group1 <= 99)
		#assert (digit_group2!=None) and (00 <= digit_group2 <= 199)

		# Light up segments for the corresponding digit
		if digit_group1 != None:
			u,t,h = self.decompose( digit_group1 )
			self.set_digit( 0, u )
			self.set_digit( 1, t )
			# None
		if digit_group2 != None:
			u,t,h = self.decompose( digit_group2 )
			self.set_digit( 2, u )
			self.set_digit( 3, t )
			# Light for Hundreds
			self.set_digit( 4, h )

	def clear( self, digit_group_index=None ):
		# Clear the digit group 1 or 2
		if (digit_group_index==1) or (digit_group_index==None):
			self.set_digit( 0, None )
			self.set_digit( 1, None )
		if (digit_group_index==2) or (digit_group_index==None):
			self.set_digit( 2, None )
			self.set_digit( 3, None )
			self.set_digit( 4, None )

	def int( self, value ):
		""" Display an integer value from 0 to 19999 """
		assert 0<=value<=19999
		# Clear the digits
		self.clear( 1 ) 
		self.clear( 2 )
		# Clear separator
		self.separator = None
		# Display the value
		self.set( digit_group2=value // 100 if value > 99 else None, digit_group1=value%100)

	def float( self, value ):
		""" Display an integer value from 0 to 199.99 """
		assert 0<=value<=199.99
		self.clear( 1 )
		self.clear( 2 )
		# Set separator
		self.separator = DOT
		# Display the value
		self.set( digit_group2=int(value), digit_group1 = int((value-int(value))*100) )


class DiskPanel( BasePanel ):
	def __init__( self, owner, segments ):
		super().__init__( owner, segments )
		self._root = [8,0] # Root of each number (1rst segment of each digit, from left to right)
		self._point = 15 # (on top) and 16 (on the bottom)
		self._discsegs = [17,18,19,20,21,22,23,24,25,26]
		self._rotate_clear()

	def _rotate_clear( self ):
		self._is_rotating = False
		self._rotate_positive = True
		self._rotate_pos = 0 # _discsegs index		

	def set( self, digit_group ):
		""" Allows to set the digits segments. Group 1 is on the right, group 2 on the left """
		assert 00 <= digit_group <= 99

		# Light up segments for the corresponding digit
		u,t,h = self.decompose( digit_group )
		self.set_digit( 0, u )
		self.set_digit( 1, t )

	def clear( self ):
		""" Clear the displayed digits """
		self.set_digit( 0, None )
		self.set_digit( 1, None )

	def disc( self, state=True ):
		""" Display of hide the disc """
		for seg_id in self._discsegs:
			self._seg.set( seg_id, state )
		if not( state ):
			self._rotate_clear()

	def disc_start( self, positive=True ):
		""" Start positive or negative disc rotation """
		self.disc( state=positive )
		self._is_rotating = True
		self._rotate_positive = positive
		self._rotate_pos = 0 # _discsegs index
		self.disc_step()

	def disc_step( self ):
		assert self._is_rotating
		# Invert current segment
		if self._rotate_positive:
			# Light-up current segment
			# Turn-off next segment
			self._seg.set( self._discsegs[self._rotate_pos], True )
			self._rotate_pos += 1
			if self._rotate_pos >= len( self._discsegs ):
				self._rotate_pos = 0
			self._seg.set( self._discsegs[self._rotate_pos], False )
		else:
			# turn of the current segment
			# Turn-on the next segment
			self._seg.set( self._discsegs[self._rotate_pos], False )
			self._rotate_pos += 1
			if self._rotate_pos >= len( self._discsegs ):
				self._rotate_pos = 0
			self._seg.set( self._discsegs[self._rotate_pos], True )


class VFD_Proximus( VFD_PT6302 ):
	""" Specialized VFD_PT6302 for Proximus display """
	def __init__( self, sck_pin, sdata_pin, cs_pin, reset_pin=None, digits=15 ):
		if reset_pin != None:
			_reset = Pin( reset_pin, Pin.OUT, value=True ) # Unactive
		else:
			_reset = None
		_cs    = Pin( cs_pin, Pin.OUT, value=True ) # unactiva
		_sdata = Pin( sdata_pin, Pin.OUT )
		_sck   = Pin( sck_pin, Pin.OUT, value=True )
		super().__init__( _sck, _sdata, _cs, _reset, digits )
		self._options = set([])
		self._seg1 = self.attach_digit( 1, RAM5 ) # Seg of digit 1
		self._seg2 = self.attach_digit( 2, RAM6 ) # Seg of digit 2
		self._seg3 = self.attach_digit( 3, RAM7 ) # Seg of digit 2
		self._left_panel = DigitalPanel( self, self._seg1 )
		self._center_panel = DigitalPanel( self, self._seg2 )
		self._right_panel  = DiskPanel( self, self._seg3 )
		self.options = OptionSet( self, [] )


	def clrscr( self ):
		""" Clear the Text zone """
		self.display_digit( 3, " "*13 )

	def print( self, text, from_pos=1 ):
		""" Draw a text on the screen from position 1 to 12 """
		max_len = 12 - (from_pos-1)
		self.display_digit( from_pos+3, text[:max_len] ) # Displat starts at Digit 4

	@property
	def center( self ):
		""" Center Digital Panel """
		return self._center_panel

	@property
	def left( self ):
		""" Left Digital Panel """
		return self._left_panel

	@property
	def right( self ):
		""" Right Digital Panel (with the rotating disk)"""
		return self._right_panel

	def update( self ):
		""" Update the Symbols on  VFD """
		self._seg1.set( 32,   TITLE in self.options )
		self._seg1.set( 24, CHANNEL in self.options )
		self._seg1.set( 7,    TRACK in self.options )

		self._seg2.set( 32,      AM in self.options )
		self._seg2.set( 34,      FM in self.options )

		self._seg3.set( 27,  STEREO in self.options )
		self._seg3.set( 28,  RECORD in self.options )
		self._seg3.set( 32,   CLOCK in self.options )
		self._seg3.set( 33, ANTENNA in self.options )

		self._seg1.update()
		self._seg2.update()
		self._seg3.update()

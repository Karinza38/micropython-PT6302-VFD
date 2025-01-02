
"""
  vfd_pt63.py is a micropython module for PT6302 VFD driver (Vaccum Fluorescent Display)

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
import time
from micropython import const

RAM0 = const(0) # Char identification in CGRAM Character Graphic Ram
RAM1 = const(1) 
RAM2 = const(2)
RAM3 = const(3)
RAM4 = const(4)
RAM5 = const(5)
RAM6 = const(6)
RAM7 = const(7)

class DigitSegments:
	def __init__( self, owner, digit_idx, ram_idx ):
		""" owner is the VFD_M6604 class """
		assert RAM0 <= ram_idx <= RAM7
		self.owner = owner
		self.digit_idx = digit_idx
		self.ram_idx = ram_idx
		self.clear()

	def clear( self ):
		self.data = [ 0b00100000 | self.ram_idx , 0b0, 0b0, 0b0, 0b0, 0b0 ]

	def set( self, seg, value ):
		assert 0 <= seg <= 34, "seg must be from 0 to 34"
		seg = 34-seg
		bit_shift = 6-((seg) // 5) # 7..0
		byte_index = 6-(1+(seg % 5))   # 1..6 (0 is reserved)

		_d = self.data[ byte_index ]
		if value: # Set the bit
			_d |= 1<<bit_shift
		else: # clear the bit
			_d &= (0xFF ^ (1<<bit_shift))
		# Store the updated data
		self.data[ byte_index ] = _d
		#print(self.data)

	def update( self ):
		""" Update the LCD @ char_index """
		self.owner.send_cmd( self.data ) # Store display flags in the related RAM index
		self.owner.display_digit( self.digit_idx, self.ram_idx ) # display the RAM idx character


class VFD_PT6302():
	""" PT6302 Vaccum Fluorescent Display driver """
	def __init__( self, sck, sdata, cs, reset=None, digits=15 ):
		self.sck = sck
		self.sdata = sdata
		self.cs = cs
		self.reset = reset
		self.digits = digits # Number of digits

		self.cs.value( True ) # disable
		if self.reset != None:
			self.reset.value( False ) # Do reset
			time.sleep_ms( 20 )
			self.reset.value( True ) 
			time.sleep_ms( 10 )

		self.output_port_set( True, False )
		self.normal_operation()
		self.digit_length( self.digits )
		self.display_duty( 7 ) # 0: minimum brightness, 7: max brightness
		self.clear()

	def send( self, arr ):
		# bit banging send of bytes/byteArray content (bit-banging)
		self.cs.value( 0 ) # Active Low
		for data in arr:
			#print( data, bin(data) )
			for i in range( 8 ): # LSBF
				self.sck.value( 0 )
				mask = 1<<i
				self.sdata.value( (data & mask)==mask ) # set state of bit
				#time.sleep_ms( 1 )
				self.sck.value( 1 ) # rising edge for data acquisition
				#time.sleep_ms( 1 )
		self.cs.value( 1 )

	def send_cmd( self, val_or_list ):
		# convert the given value or a list of value to bytes and send it to the lcd
		if type(val_or_list) is list:
			self.send( bytes(val_or_list) )
		else:
			self.send( bytes([val_or_list]) )


	def cmd_all_digit( self, state ):
		""" return the byte with the command value. state value are True=ALL_ON, False=ALL_OFF, None=normal operation """
		if state == None:
			return 0b01110000
		elif state:
			return 0b01110011
		else:
			return 0b01110001

	def cmd_digit_len( self, value ):
		assert 9<=value<=16
		self.digits = value
		bit_values = [ 0b001, 0b010, 0b011, 0b100, 0b101, 0b110, 0b111, 0b000 ] # K0,K1,K2 bits for 9 digits to 16 digits

		bit_val = bit_values[ value-9 ]
		return 0b01100000 | bit_val


	# Commands

	def all_digit_on( self ):
		""" Set all digit ON (for debugging purpose) """
		self.send_cmd( self.cmd_all_digit(True) )

	def all_digit_off( self ):
		""" Set all digit OFF (for debugging purpose) """
		self.send_cmd( self.cmd_all_digit(False) )

	def normal_operation( self ):
		""" return to normal operation after a all_digit( xxxx ) call """
		self.send_cmd( self.cmd_all_digit(None) )

	def digit_length( self, value ):
		""" Length of display in digits (used by auto incrementation) """
		self.send_cmd( self.cmd_digit_len(value) )

	def output_port_set( self, port1=False, port2=False ):
		_val = 0b01000000
		if port1:
			_val |= 0b1
		if port2:
			_val |= 0b10
		self.send_cmd( _val )

	def display_duty( self, duty ):
		assert 1<=duty<=8
		self.send( [0b01010000 | (duty-1)] )

	def clear( self ):
		self.display_digit( 1, list([0x20 for i in range(self.digits)]) )


	def display_digit( self, position, data ):
		# Display an integer(8bit) or string or list[int]
		assert type(data) in (int,str,list)
		assert 1<=position<=16
		_l = [ 0b00010000 | (position-1) ]
		if type(data) is int:
			assert data < 256
			_l.append( data )
		elif type(data) is list:
			_l.extend( data )
		else:
			_l.extend( data.encode('ASCII') )
		self.send_cmd( _l )


	def define_char( self, ram_idx, char_def ):
		""" Define a 5 x 7 character in RAM char. char_idx is a RAMx constant.
		    char_def is a list define 7 lines of 5 bit wide each.
		    [ 0b00000, 0b01010, 0b10101, 0b10001, 0b01010, 0b00100, 0b00000 ]  """
		assert RAM0 <= ram_idx <= RAM7
		assert (type(char_def) is list) and (len(char_def)==7), "char_def list must have 7 items of 5bits each"
		_data = [ 0b00100000 | ram_idx ]
		for bit_shift in range(4,-1,-1): # 4..0
			_val = 0
			bit_mask = 1 << bit_shift
			for row in range(6,-1,-1): # 6..0
				_val = _val + (1 if (char_def[row] & bit_mask)==bit_mask else 0)
				
				_val = _val << 1 # Bit 0 is not relevant

			_val = _val >> 1 # For PT6302, it is the bit 7 that is not relevant
			_data.append( _val )
		self.send_cmd( _data )

	def attach_digit( self, digit_idx, ram_idx ):
		""" create a DigiSegments instance linked to a Digit position. the segments on/off are controled via the ram_idx custom characters """		
		assert 0<=digit_idx<=self.digits
		assert RAM0 <= ram_idx <= RAM7
		_segments = DigitSegments( self, digit_idx, ram_idx )
		_segments.clear()
		return _segments

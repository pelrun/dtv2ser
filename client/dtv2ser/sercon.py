#
# sercon.py - serial low level connection
#
# Written by
#  Christian Vogelgsang <chris@vogelgsang.org>
#
# This file is part of dtv2ser.
# See README for copyright notice.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
#  02111-1307  USA.
#

# requires PySerial from http://pyserial.sourceforge.net !

import serial
import time
import sys

from dtv2ser.status import *

class SerCon:
  """Encapsulates a low level serial connection to a dtv2ser server device."""

  # time out to wait for server become ready
  ready_timeout = 5

  def __init__(self, serial_port, serial_baud, serial_timeout=2):
    """Open a serial connection to the dtv2ser server."""
    try:
      print "port {} baud {}".format(serial_port,serial_baud)
      self.ser = serial.Serial(port=serial_port,
                              baudrate=serial_baud,
                              bytesize=serial.EIGHTBITS,
                              parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE,
                              timeout=serial_timeout,
                              writeTimeout=serial_timeout,
                              xonxoff=0,
                              rtscts=1,
                              dsrdtr=0)
      if self.ser.isOpen():
        self.ser.flushInput()
        self.ser.flushOutput()
        self.valid = True
      else:
        self.valid = False
    except:
      self.valid = False

  def __del__(self):
    """Close connection to dtv2 server."""
    if self.valid and self.ser.isOpen():
      self.ser.close()

  def is_connected(self):
    """Is client connected?
    Returns True if the server is ready, otherwise False.
    """
    return self.valid and self.ser.isOpen()

  # ----- basic I/O -----

  def receive_data(self,length):
    """Read n bytes from server.
    Returns (result,data).
    """
    result = self.ser.read(length)
    if len(result) != length:
      return (CLIENT_ERROR_SERVER_TIMEOUT,result)
    return (STATUS_OK,result)

  def send_data(self,data):
    """Write n bytes to server.
    Returns result.
    """
    try:
      self.ser.write(data)
    except serial.SerialException:
      return CLIENT_ERROR_SERVER_TIMEOUT
    return STATUS_OK

  def wait_for_data(self,timeout=0,sleep=0.1):
    """Wait for server to send us some data
    Returns result code.
    """
    if timeout == 0:
      timeout = self.ready_timeout
    steps = int(timeout / sleep)
    for t in xrange(steps):
      if self.ser.in_waiting > 0:
        return STATUS_OK
      time.sleep(sleep)
    return CLIENT_ERROR_SERVER_TIMEOUT

  # ----- block transfers -----

  def dump_cts(self,num):
    for a in xrange(num):
      isCTS = self.ser.getCTS()
      if isCTS:
        print "*",
      else:
        print "-",
      sys.stdout.flush()
      time.sleep(0.1)
    print

  def calc_crc16(self,data):
    """Calc a block checksum with crc16.
    Return crc16.
    """
    crc = 0xffff
    for a in data:
      b = ord(a)
      crc ^= b;
      for i in xrange(8):
        if crc & 1:
          crc = (crc >> 1) ^ 0xA001
        else:
          crc = (crc >> 1)
    return crc & 0xffff

  def check_block(self,data,crc16):
    """Check CRC16 of a block
    Returns status
    """
    my_crc16 = self.calc_crc16(data)
    if crc16!=my_crc16:
      return CLIENT_ERROR_CRC16_MISMATCH
    else:
      return STATUS_OK;

  def receive_block(self,start,length,block_size,callback=lambda x:True):
    """Receive a large block of data in blocks given by block_size.
    Use optional callback to get feedback while transfer.
    Returns (result,duration,data).
    """
    status = STATUS_OK
    pos = 0
    data = ''

    # begin upload
    start_time = time.time()

    # write start byte
    status = self.send_data(chr(0))
    if status != STATUS_OK:
      return status

    # transfer blocks
    while length > 0:
      callback(pos)

      offset = start & 0x3fff
      spare  = 0x4000 - offset
      get_len = min(length,block_size,spare)

      # receive block
      status,raw = self.receive_data(get_len)
      if status!=STATUS_OK:
        break

      # receive crc16
      status,crc16raw = self.receive_data(2)
      if status!=STATUS_OK:
        break

      # convert block length
      try:
        crc16  = ord(crc16raw[0]) * 256 + ord(crc16raw[1])
      except:
        status = CLIENT_ERROR_INVALID_HEX_NUMBER
        break

      # block end
      status = self.check_block(raw,crc16)
      if status!=STATUS_OK:
        break

      data += raw
      pos += get_len
      length -= get_len
      start += get_len

    # write end byte
    if status != STATUS_OK:
      end_byte = 0x01
    else:
      end_byte = 0x00
    self.send_data(chr(end_byte))

    if end_byte == 0x01:
      while self.ser.in_waiting>0:
          self.ser.flushInput()
          time.sleep(0.5)

    # end upload
    end_time = time.time()

    # all ok
    return (status,end_time - start_time,data)

  def send_block(self,start,data,block_size,callback=lambda x:True):
    """Send a large block of data in blocks given by block_size.
    Use optional callback to get feedback while transfer.
    Returns (result,duration).
    """
    status = STATUS_OK
    length = len(data)
    pos = 0

    # begin upload
    start_time = time.time()

    # get start byte
    status,start_byte = self.receive_data(1)
    if status != STATUS_OK:
      return status,0
    if ord(start_byte[0]) != 0:
      return CLIENT_ERROR_CORRUPT_SERIAL_DATA,0

    # transfer blocks
    while length > 0:
      callback(pos)

      offset = start & 0x3fff
      spare  = 0x4000 - offset
      put_len = min(length,block_size,spare)

      # now send block
      raw = data[pos:pos+put_len]
      status = self.send_data(raw)
      if status != STATUS_OK:
        break

      # calc crc16
      crc = self.calc_crc16(raw)
      crc_raw = chr((crc >> 8)&0xff) + chr(crc & 0xff)
      status = self.send_data(crc_raw)
      if status != STATUS_OK:
        break;

      # got an error byte?
      if self.ser.in_waiting > 0:
        break

      pos += put_len
      length -= put_len
      start += put_len

    # an error occured - abort
    if status != STATUS_OK:
      return status,0

    # read end byte
    status,end_byte = self.receive_data(1)
    if status != STATUS_OK:
      return status,0

    # end byte ok?
    if ord(end_byte[0]) != 0:
      return TRANSFER_ERROR_VERIFY_MISMATCH,0

    end_time = time.time()

    # all ok
    return (status,end_time - start_time)

  # ---------- boot command -------------------------------------------------

  def send_boot(self,start,data,callback=lambda x:True):
    """Send data with boot protocol
       Returns (result,duration)
    """

    # begin upload
    start_time = time.time()

    # get start byte
    status,start_byte = self.receive_data(1)
    if status != STATUS_OK:
      return status,0
    start_code = ord(start_byte)
    if start_code != 0:
      return CLIENT_ERROR_CORRUPT_SERIAL_DATA,0

    # write data
    length = len(data)
    chk = 0
    for pos in xrange(length):
      callback(pos)

      # already replied? (with error status)
      if self.ser.in_waiting > 0:
        break

      # now send data
      status = self.send_data(data[pos])
      if status != STATUS_OK:
        break

      # calc check sum
      chk += 1 + ord(data[pos])

    # get status byte
    status,status_byte = self.receive_data(1)
    if status != STATUS_OK:
      return status,0
    status_code = ord(status_byte[0])
    if status_code != STATUS_OK:
      return TRANSFER_ERROR_MASK | status_code,0;

    # get check sum
    status,check_byte = self.receive_data(1)
    if status != STATUS_OK:
      return status,0
    check_code = ord(check_byte[0])
    chk &= 0xff

    # check sum
    if check_code != (chk & 0xff):
      return CLIENT_ERROR_CORRUPT_SERIAL_DATA,0

    end_time = time.time()
    return STATUS_OK,(end_time-start_time)

  # ---------- joy stream ---------------------------------------------------

  def send_joy_stream(self,data,callback=lambda x:True):
    """Send a stream of bytes as a joy stream.
      First you issue a 'js' joy stream command and then this routine is
      called to send the joy stream command bytes.
      You must terminate the stream with 0x80 (END)
      Returns result,time
    """

    # begin upload
    start_time = time.time()

    expected_duration = 0.0

    # get start byte
    status,start_byte = self.receive_data(1)
    if status != STATUS_OK:
      return status,0
    start_code = ord(start_byte)
    if start_code != 0:
      return CLIENT_ERROR_CORRUPT_SERIAL_DATA,0

    for pos in xrange(len(data)):
      # call function to get next command
      c = data[pos]
      callback(pos)

      # send a joy stream command
      # ignore timeouts entirely
      while True:
        result = self.send_data(c)
        if result == STATUS_OK:
            break

      # END command?
      if ord(c) & JOY_COMMAND_MASK == JOY_COMMAND_EXIT:
        break

      if ord(c) & JOY_COMMAND_MASK == JOY_COMMAND_WAIT:
          expected_duration += float(ord(c) & ~JOY_COMMAND_MASK)/100

      # does the server already sent a status byte?
      if self.ser.in_waiting > 0:
        break

    # give other end time to execute joystream
    while ((time.time() - start_time) < expected_duration):
        if (self.ser.in_waiting > 0):
            break

    # get status byte from server
    result,data = self.receive_data(1)
    if result != STATUS_OK:
      return result,0

    # make sure status was 0 (OK)
    if ord(data) != 0:
      return CLIENT_ERROR_SERVER_NOT_READY,0

    end_time = time.time()
    return STATUS_OK,(end_time - start_time)


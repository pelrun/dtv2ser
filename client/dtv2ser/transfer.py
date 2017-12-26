#
# transfer.py - send and receive data
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

import time

from dtv2ser.status  import *
from dtv2ser.cmdline import CmdLine
from dtv2ser.sercon  import SerCon
from dtv2ser.param   import Param

class Transfer:
  """Transfer command handling tools."""

  # how long to wait for the server after a transfer operation
  server_ready_timeout = 500

  # how many retries to get the transfer result after a transfer operation
  get_result_retries = 20

  def __init__(self,con):
    """Create a new transfer object."""
    # get cmdline
    self.con = con
    self.cmdline = CmdLine(con)
    # init transfer rate
    self.server_tx_rate = 0
    self.server_rx_rate = 0
    self.client_tx_rate = 0
    self.client_rx_rate = 0

  # ---------- block size ---------------------------------------------------

  def set_block_size(self,block_size):
    """Set block_size parameter
    Returns the result code
    """
    param = Param(self.con)
    print "\t[set new blocksize: %04x]" % block_size
    return param.set_word(PARAM_WORD_DTV_TRANSFER_BLOCK_SIZE,block_size)

  def get_block_size(self):
    """Get the block_size parameter
    Returns (result,block_size)
    """
    param = Param(self.con)
    return param.get_word(PARAM_WORD_DTV_TRANSFER_BLOCK_SIZE)

  def ensure_block_size(self,block_size):
    """Make sure the given size is set in the dtv2ser device
    Returns result
    """
    result,has_size = self.get_block_size()
    if result != STATUS_OK:
      return result
    if has_size != block_size:
      return self.set_block_size(block_size)
    else:
      return STATUS_OK

  # ---------- transfer mode ------------------------------------------------

  def set_transfer_mode(self,mode):
    """Issue a 'm' command to set the transfer mode
    Returns the result code
    """
  #print "\t[transfer mode=%2d]" % mode
    return self.cmdline.do_command("m%02x" % mode)

  # ---------- transfer result ----------------------------------------------

  def get_transfer_result(self):
    """Issue a 't' command to get the result
    Returns result code and transfer time
    """
    result = self.cmdline.do_command("t")
    if result != STATUS_OK:
      return (result,0)

    # get transfer result
    (result,transfer_result) = self.cmdline.get_byte()
    if result != STATUS_OK:
      return (result,0)
    elif transfer_result != STATUS_OK:
      return (transfer_result | TRANSFER_ERROR_MASK,0)

    # get transfer time
    (result,transfer_time) = self.cmdline.get_word()
    if result != STATUS_OK:
      return (result,transfer_time)
    else:
      return (STATUS_OK,transfer_time)

  def wait_for_transfer_result(self):
    """Wait until the transfer result is available or a time out occurs
    Returns result code and transfer time
    """

    # wait a bit for the result
    for x in xrange(self.get_result_retries):
      result,transfer_time = self.get_transfer_result()
      # everything is ok... return
      if result == STATUS_OK:
        return (STATUS_OK,transfer_time)
      # a transfer error occured -> report it!
      if result & TRANSFER_ERROR_MASK == TRANSFER_ERROR_MASK:
        return (result,time)
      # any other error: retry
      time.sleep(0.1)

    # client timed out
    return (CLIENT_ERROR_SERVER_TIMEOUT,0)

  # ---------- transfer tools -----------------------------------------------

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

  def update_server_tx_rate(self,length,server_time):
    """Get transfer time from server and calculate the tx rate.
    Return result.
    """
    if server_time > 0:
      self.server_tx_rate = length * 100.0 / (server_time * 1024.0)
    else:
      self.server_tx_rate = 0

  def update_server_rx_rate(self,length,server_time):
    """Get transfer time from server and calc transfer rate
    Return result.
    """
    if server_time > 0:
      self.server_rx_rate = length * 100.0 / (server_time * 1024.0)
    else:
      self.server_rx_rate = 0

  def update_client_tx_rate(self,length,duration):
    """Update the server transfer rate from the
    """
    if duration != 0:
      self.client_tx_rate = length / (duration * 1024.0)
    else:
      self.client_tx_rate = 0

  def update_client_rx_rate(self,length,duration):
    """After a receive transfer update statistics
    """
    if duration != 0:
      self.client_rx_rate = length / (duration * 1024.0)
    else:
      self.client_rx_rate = 0

  # ---------- block transfer commands --------------------------------------

  def do_send_boot(self,start,data,callback=lambda x:True):
    """Transmit via boot protocol"""
    # send command
    cmd = "b%04x%04x" % (start,len(data))
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result

    result,duration = self.con.send_boot(start,data,callback)
    if result != STATUS_OK:
      return result

    # check transfer result
    result,server_time = self.wait_for_transfer_result()
    if result != STATUS_OK:
      return result

    # update tx rate
    length = len(data)
    self.update_client_tx_rate(length,duration)
    self.update_server_tx_rate(length,server_time)

    return STATUS_OK

  def do_send_command(self,cmd,start,data,callback=lambda x:True,block_size=0x400,mode=TRANSFER_MODE_NORMAL):
    """Transmit a send data command and upload data.
    Return result.
    """
    # send transfer mode
    result = self.set_transfer_mode(mode)
    if result != STATUS_OK:
      return result

    # ensure block size
    result = self.ensure_block_size(block_size)
    if result != STATUS_OK:
      return result

    # send command
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result

    # upload data
    (result,duration) = self.con.send_block(start,data,block_size,callback=callback)
    if result != STATUS_OK:
      return result

    # check transfer result
    result,server_time = self.wait_for_transfer_result()
    if result != STATUS_OK:
      return result

    # update tx rate
    length = len(data)
    self.update_client_tx_rate(length,duration)
    self.update_server_tx_rate(length,server_time)

    return STATUS_OK

  def do_receive_command(self,cmd,start,length,callback=lambda x:True,block_size=0x400,mode=TRANSFER_MODE_NORMAL):
    """Transmit a receive data command and download data.
    Return (result,data)
    """
    # send transfer mode
    result = self.set_transfer_mode(mode)
    if result != STATUS_OK:
      return (result,'')

    # ensure block size
    result = self.ensure_block_size(block_size)
    if result != STATUS_OK:
      return (result,'')

    # send command
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return (result,'')

    # download data
    (result,duration,data) = self.con.receive_block(start,length,block_size,callback=callback)
    if result != STATUS_OK:
      return (result,data)

    # check transfer result
    result,server_time = self.wait_for_transfer_result()
    if result != STATUS_OK:
      return (result,data)

    # update rx rate
    self.update_client_rx_rate(length,duration)
    self.update_server_rx_rate(length,server_time)

    return (STATUS_OK,data)

  # ---------- diagnose commands --------------------------------------------

  def set_diagnose_pattern(self,pattern):
    """Set the diagnose pattern in dtv2ser.
    Return result.
    """
    param = Param(self.con)
    #print "\t[set diagnose pattern=%02x]" % pattern
    return param.set_byte(PARAM_BYTE_DIAGNOSE_PATTERN,pattern)

  def get_diagnose_pattern(self):
    """Read the diagnose pattern from dtv2ser.
    Return (result,pattern).
    """
    param = Param(self.con)
    return param.get_byte(PARAM_BYTE_DIAGNOSE_PATTERN)

  def do_diagnose_command_only_dtv(self,cmd,length,is_tx,callback=lambda x:True,block_size=0x400):
    """Issue a diagnose send command but do not transfer data via serial.
    Return result.
    """
    # send transfer mode
    result = self.set_transfer_mode(TRANSFER_MODE_DTV_ONLY)
    if result != STATUS_OK:
      return result

    # ensure block size
    result = self.ensure_block_size(block_size)
    if result != STATUS_OK:
      return result

    # send command
    result = self.cmdline.do_command(cmd);
    if result != STATUS_OK:
      return result

    # wait for result
    start_time = time.time()
    result,server_time = self.wait_for_transfer_result()
    end_time = time.time()
    if result != STATUS_OK:
      return result

    # update tx or rx rate
    if is_tx:
      self.update_client_tx_rate(length,end_time - start_time)
      self.update_server_tx_rate(length,server_time)
    else:
      self.update_client_rx_rate(length,end_time - start_time)
      self.update_server_rx_rate(length,server_time)

    return STATUS_OK

  def do_diagnose_send_command_only_client(self,cmd,start,length,callback=lambda x:True,block_size=0x400):
    """Issue a diagnose send command but do not transfer to the DTV.
    Return result.
    """
    # get pattern
    status,pattern = self.get_diagnose_pattern()
    if status != STATUS_OK:
      return status

    # create test data
    data = chr(pattern) * length

    # perform send command
    return self.do_send_command(cmd,start,data,callback=callback,mode=TRANSFER_MODE_SERIAL_ONLY,block_size=block_size)

  def do_diagnose_receive_command_only_client(self,cmd,start,length,callback=lambda x:True,block_size=0x400):
    """Issue a diagnose receive command but do not transfer to the DTV.
    Return result.
    """
    # get pattern
    status,pattern = self.get_diagnose_pattern()
    if status != STATUS_OK:
      return status

    # perform receive command
    (result,data) = self.do_receive_command(cmd,start,length,callback=callback,mode=TRANSFER_MODE_SERIAL_ONLY,block_size=block_size)
    if result != STATUS_OK:
      return result

    # check data
    expected_data = chr(pattern) * length
    if expected_data != data:
      print "data mismatch:",data
      return CLIENT_ERROR_CORRUPT_SERIAL_DATA
    else:
      return STATUS_OK

  # ---------- get statistics -----------------------------------------------

  def begin_rx_rates(self):
    """Begin a rx operation"""
    self.rx_begin_time = time.time()

  def begin_tx_rates(self):
    """Begin a tx operation"""
    self.tx_begin_time = time.time()

  def get_rx_rates(self,length):
    """End rx operation and return client and server rx rates."""
    t = time.time() - self.rx_begin_time
    return (self.client_rx_rate,self.server_rx_rate,t,length)

  def get_tx_rates(self,length):
    """End tx operation and return client and server tx rates."""
    t = time.time() - self.tx_begin_time
    return (self.client_tx_rate,self.server_tx_rate,t,length)

  # ---------- joy stream ---------------------------------------------------

  def do_joy_stream(self,stream,callback=lambda x:True):
    """Send a joy stream given in string stream
       Returns status,duration"""
    result = self.cmdline.do_command("j")
    if result != STATUS_OK:
      return result

    return self.con.send_joy_stream(stream,callback)

  def do_joy_stream_seq(self,stream_seq,callback=lambda x:True):
    """Send a sequence of joy streams
       Returns status."""
    total_duration = 0
    for js in stream_seq:
      cmd = js[0]

      # send a joy stream
      if cmd == JoyStream_Commands:
        result = self.cmdline.do_command("j")
        if result != STATUS_OK:
          return result,0
        result,duration = self.con.send_joy_stream(js[1],callback)
        if result != STATUS_OK:
          return result,0
        total_duration += duration
      # sleep some seconds
      elif cmd == JoyStream_Sleep:
        duration = js[1]
        time.sleep(duration)
      else:
        print "UNKNOWN Joy Stream Command"

    return STATUS_OK,total_duration

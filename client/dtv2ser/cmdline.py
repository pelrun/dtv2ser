#
# cmdline.py - low level command line protocol of dtv2ser server
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

from dtv2ser.sercon import *
from dtv2ser.status import *

class CmdLine:
  """Handle low level command line protocol of dtv2ser server."""

  def __init__(self,con):
    """Setup command line handler with connection object"""
    self.con = con

  def wait_for_data(self,timeout):
    """Pass on to connection"""
    return self.con.wait_for_data(timeout)

  # ----- read result of server -----

  def get_status_byte(self):
    """Fetch a hex byte and interpret it as a status from the server
    Return result
    """
    (result,val) = self.get_byte()
    if result != STATUS_OK:
      return result
    if val == 0:
      return STATUS_OK
    return val | TRANSFER_ERROR_MASK

  def get_output_bytes(self,num):
    """Read num hex bytes and a linefeed
    Return (result,[outbytes])
    """
    output = []
    (result,data) = self.con.receive_data(num*2+2)
    if result != STATUS_OK:
      return (result,output)
    try:
      for i in xrange(num):
        value = int(data[i*2:i*2+2],16)
        output.append(value)

      # get status
      result = self.get_status_byte()
      return (result,output)
    except:
      return (CLIENT_ERROR_INVALID_HEX_NUMBER,output)

  def get_var_output_bytes(self):
    """Read size and output bytes
    Return (result,[outbytes])
    """
    (result,val) = self.get_byte()
    if result != STATUS_OK:
      return (result,[])
    return self.get_output_bytes(val)

  def get_byte(self):
    """Fetch a hex byte.
    Returns (result,byte)
    """
    (result,data) = self.con.receive_data(4) # xx\r\n
    if result != STATUS_OK:
        return (result,0)
    try:
      value = int(data[0:2],16)
      return (STATUS_OK,value)
    except:
      return (CLIENT_ERROR_INVALID_HEX_NUMBER,0)

  def get_word(self):
    """Fetch a hex word.
    Returns (result,word)
    """
    (result,data) = self.con.receive_data(6) # xxxx\r\n
    if result != STATUS_OK:
        return (result,0)
    try:
      value = int(data[0:4],16)
      return (STATUS_OK,value)
    except:
      return (CLIENT_ERROR_INVALID_HEX_NUMBER,0)

  def get_dword6(self):
    """Fetch a 6 hex dword.
    Returns (result,dword)
    """
    """Fetch a hex word.
    Returns (result,word)
    """
    (result,data) = self.con.receive_data(8) # xxxxxx\r\n
    if result != STATUS_OK:
        return (result,0)
    try:
      value = int(data[0:6],16)
      return (STATUS_OK,value)
    except:
      return (CLIENT_ERROR_INVALID_HEX_NUMBER,0)

  # ----- perform command -----

  def do_command(self,cmd):
    """Send a command to dtv2ser and wait for its parse result
    Returns result code
    """

    # send command
    result = self.con.send_data(cmd + '\n')
    if result != STATUS_OK:
      return result
    # exepct parse result
    (result,cmdline_result) = self.get_byte()
    if result != STATUS_OK:
      return result
    elif cmdline_result != STATUS_OK:
      return cmdline_result | CMDLINE_ERROR_MASK
    else:
      return STATUS_OK

#
# param.py - handle dtv2ser parameter commands
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

from dtv2ser.status import *
from dtv2ser.cmdline import *

class Param:
  """Handle dtv2ser parameter commands."""

  def __init__(self,con):
    # create a cmdline object from the connection
    self.cmdline = CmdLine(con)

  def dump(self):
    """Read all parameters from dtv2ser.
    Returns (result,[byte params],[word params]).
    """

    # issue a 'pq' param query command
    cmd = "pq"
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return (result,[],[])

    # get num byte params
    (result,num_byte) = self.cmdline.get_byte()
    if result != STATUS_OK:
      return (result,[],[])

    # get num word params
    (result,num_word) = self.cmdline.get_byte()
    if result != STATUS_OK:
      return (result,[],[])

    # get byte params
    byte_param = []
    for a in xrange(num_byte):
      (result,byte) = self.get_byte(a)
      if result != STATUS_OK:
        return (result,[],[])
      byte_param.append(byte)

    # get word params
    word_param = []
    for a in xrange(num_word):
      (result,word) = self.get_word(a)
      if result != STATUS_OK:
        return (result,[],[])
      word_param.append(word)

    # check param size with host params
    if len(byte_param) != len(param_byte_name):
      return (CLIENT_ERROR_PARAM_SIZE_MISMATCH,[],[])
    if len(word_param) != len(param_word_name):
      return (CLIENT_ERROR_PARAM_SIZE_MISMATCH,[],[])

    return (STATUS_OK,byte_param,word_param)

  def do_param_command(self,cmd):
    """Issue a parameter command.
    Return result.
    """
    # issue command
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result

    # read command result
    (result,data) = self.cmdline.get_byte()
    if result != STATUS_OK:
      return result

    # check parameter result
    if data == STATUS_OK:
      return STATUS_OK
    else:
      return data | PARAMETER_ERROR_MASK;

  def load(self):
    """Load parameters from EEPROM.
    Return result.
    """
    return self.do_param_command("pc01")

  def save(self):
    """Save parameters to EEPROM.
    Return result.
    """
    return self.do_param_command("pc02")

  def reset_default(self):
    """Reset parameters to default values.
    Return result.
    """
    return self.do_param_command("pc00")

  def set_byte(self,num,val):
    """Set a byte parameter.
    Return result.
    """
    cmd = "pbs%02x%02x" % (num,val)
    return self.do_param_command(cmd)

  def set_word(self,num,val):
    """Set a word parameter.
    Return result.
    """
    cmd = "pws%02x%04x" % (num,val)
    return self.do_param_command(cmd)

  def get_byte(self,num):
    """Get a byte parameter.
    Returns (result,byte).
    """
    cmd = "pbg%02x" % num
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return (result,0)
    return self.cmdline.get_byte()

  def get_word(self,num):
    """Get a word parameter.
    Returns (result,word).
    """
    cmd = "pwg%02x" % num
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return (result,0)
    return self.cmdline.get_word()

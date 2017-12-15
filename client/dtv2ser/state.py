#
# state.py - handle the state of a dtvtrans connection
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

class State:

  # state flags (can be or'ed together)
  SERVER_IS_ALIVE   = 1
  DTVTRANS_V10      = 2
  DTVTRANS_IN_RAM   = 4

  def __init__(self,dtvcmd,verbose=True):
    """Init with dtvtrans command object"""
    self.dtvcmd = dtvcmd
    self.uptodate = False
    self.state = 0
    self.verbose = verbose

  def determine(self):
    """Determine state of dtvtrans if its not up to date
    Returns STATUS_OK if state can be determined
    """
    if self.uptodate:
      return True
    self.state = 0

    # check presence first
    if self.verbose:
      print "\tstate: checking is alive"
    result = self.dtvcmd.is_alive()
    if result == TRANSFER_ERROR_NOT_ALIVE:
      return STATUS_OK
    if result != STATUS_OK:
      return result
    # ok, server is alive
    self.state |= self.SERVER_IS_ALIVE

    # check revision
    if self.verbose:
      print "\tstate: checking revision"
    (result,major,minor) = self.dtvcmd.query_revision()
    if result != STATUS_OK:
      return result
    if major == 1:
      self.state |= self.DTVTRANS_V10

      # finally check mode (in dtvtrans 1.0)
      if self.verbose:
        print "\tstate: checking mode"
      (result,port,mode,start,end) = self.dtvcmd.query_config()
      if result != STATUS_OK:
        return result
      if mode==0:
        self.state |= self.DTVTRANS_IN_RAM

    if self.verbose:
      print "\tstate:",self.to_string(self.state)
    self.uptodate = True
    return STATUS_OK

  def invalidate(self):
    """Some external event changed the state and thus invalidate it"""
    self.uptodate = False

  def get(self):
    """Check if the requested state is available.
    Returns result,state
    """
    if not self.uptodate:
      result = self.determine()
    else:
      result = STATUS_OK
    return result,self.state

  def to_string(self,state):
    if (state & self.SERVER_IS_ALIVE) == 0:
      return "no server is alive"
    if (state & self.DTVTRANS_V10) == 0:
      return "pre 1.0 dtvtrans running"
    if (state & self.DTVTRANS_IN_RAM) == 0:
      return "dtvtrans 1.0 (not running in RAM)"
    return "dtvtrans 1.0 running in RAM"


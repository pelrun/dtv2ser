#
# app.py - main application object
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

import os
import glob
import time

import dtv2ser.sercon
import dtv2ser.command
from dtv2ser.state import State
from dtv2ser.status import *
from dtv2sertool.iotools import IOTools
from dtv2sertool.helper import Helper

class AppError:
  pass

class App:

  # options of application
  serial_port = ''
  serial_speed = 230400
  serial_timeout = 5
  verbose = False
  block_size = 0x400
  # state handling
  ignore_state = False
  force_old = False

  def __init__(self):
    '''init globals from environment before parsing command line options'''
    if os.environ.has_key('DTV2SER_PORT'):
      self.serial_port = os.environ['DTV2SER_PORT']
    if os.environ.has_key('DTV2SER_SPEED'):
      self.serial_speed = int(os.environ['DTV2SER_SPEED'])
    if os.environ.has_key('DTV2SER_TIMEOUT'):
      self.serial_timeout = int(os.environ['DTV2SER_TIMEOUT'])

    # init runtime objects
    self.sercon = None
    self.dtvcmd = None
    self.state  = None
    self.iotools = IOTools()
    self.helper  = None

  def detect_serial_port(self):
    '''detect serial port if none is set'''
    if os.name == 'posix':
      if os.uname()[0] == 'Darwin':
        ports = glob.glob("/dev/cu.usbserial-*")
        if len(ports)==0:
          return '/dev/cu.dtv2ser'
        else:
          return ports[0]
      elif os.uname()[0] == 'Linux':
        return '/dev/ttyUSB0'
    elif os.name == 'nt':
      return 'com5'
    else:
      return ''

  def check_device(self):
    '''check version of firmware and client'''
    for retry in range(0,5):
        (result,server_major,server_minor) = self.dtvcmd.get_server_version()
        if result == STATUS_OK:
            break
    if result != STATUS_OK:
      self.iotools.print_result(result)
      return False
    (client_major,client_minor) = self.dtvcmd.get_client_version()
    print "dtv2sertrans version %d.%d, dtv2ser device version %d.%d" \
        % (client_major,client_minor,server_major,server_minor)
    if not self.dtvcmd.is_compatible_version(server_major,server_minor):
      print "ERROR: client is not compatible to firmware. please update!"
      return False
    return True

  def check_server(self):
    found_server = False
    result = self.dtvcmd.is_alive()
    if result == STATUS_OK:
      (result,revision) = app.dtvcmd.query_revision_string()
      if result == STATUS_OK:
        (result,impl) = app.dtvcmd.query_implementation()
        if result == STATUS_OK:
          (result,port,mode,start,end) = app.dtvcmd.query_config()
          if result == STATUS_OK:
            print "dtvtrans server version %s (%s via %s in %s)" \
              % (revision,impl,("joy1","joy2","usr")[port],("RAM","ROM")[mode])
            found_server = True
    if not found_server:
      print "dtvtrans server NOT responding!!"
    return found_server

  def post_init(self):
    '''final init after parsing global command line options'''
    if self.serial_port == '':
      self.serial_port = self.detect_serial_port()
    if self.verbose:
      print "  serial port=%s speed=%d timeout=%d" % (self.serial_port,self.serial_speed,self.serial_timeout)

    # setup serial
    self.sercon = dtv2ser.sercon.SerCon(self.serial_port,self.serial_speed,serial_timeout=self.serial_timeout)
    if not self.sercon.is_connected():
      print "ERROR: opening serial port '%s'!" % self.serial_port
      return False

    # setup dtv command object
    self.dtvcmd = dtv2ser.command.Command(self.sercon)

    # setup state
    self.state = self.dtvcmd.state

    # setup helpder
    self.helper = Helper(self.dtvcmd,self.iotools,self.verbose,self.block_size)

    # propagate verboseness to iotools
    self.iotools.verbose = self.verbose
    self.state.verbose = self.verbose

    # check device
    if not self.check_device():
      return False

    return True

  # ---------- state checks -------------------------------------------------

  def is_server_alive(self):
    if self.ignore_state:
      return True

    result,has_state = self.state.get()
    if result != STATUS_OK:
      self.iotools.print_result(result)
      return False
    return has_state & State.SERVER_IS_ALIVE

  def require_server_alive(self):
    """Make sure the server is alive."""
    if self.is_server_alive():
      return True
    print "ERROR: dtvtrans server is not alive!"
    return False

  def has_dtvtrans_10(self):
    """Check if dtvtrans 1.0 is running"""
    if self.force_old:
      return False
    if self.ignore_state:
      return True

    result,has_state = self.state.get()
    if result != STATUS_OK:
      self.iotools.print_result(result)
      return False
    return has_state & State.DTVTRANS_V10

  def require_dtvtrans_10(self):
    """Make sure the server is a 1.0"""
    if self.has_dtvtrans_10():
      return True
    print "ERROR: dtvtrans server is not v1.0!"
    return False

  def has_dtvtrans_10_in_ram(self):
    """Check if dtvtrans 1.0 is running in RAM"""
    if self.ignore_state:
      return True
    if not self.has_dtvtrans_10():
      return False

    result,has_state = self.state.get()
    if result != STATUS_OK:
      self.iotools.print_result(result)
      return False

    return has_state & State.DTVTRANS_IN_RAM

  def require_dtvtrans_10_in_ram(self):
    """Make sure the server is a 1.0 and running in RAM"""
    if self.has_dtvtrans_10_in_ram():
      return True
    print "ERROR: dtvtrans server is not in RAM! Use 'server ram' first."
    return False


# create main instance
app = App()

# define global options
global_options = [
  ("p","<port>","specify the serial port\nor use DTV2SER_PORT env variable"),
  ("s","<speed>","specify the serial speed\nor use DTV2SER_SPEED env variable"),
  ("t","<timeout>","specify the serial timeout\nor use DTV2SER_TIMEOUT env variable"),
  ("r",None,"force raw file I/O\n(automatically used for: *.raw *.bin)"),
  ("l",None,"force prg file I/O\n(automatically used for: *.prg)"),
  ("v",None,"be more verbose"),
  ("b","<block_size>","set block size for transfers (default: 0x400)"),
  ("i",None,"ignore state of dtvtrans server before executing commands"),
  ("f",None,"force old pre 1.0 dtvtrans protocol")
]

def set_global_option(key,value):
  '''set a global option from the command line'''
  if key == '-p':
    app.serial_port = value
  elif key == '-s':
    app.serial_speed = int(value)
  elif key == '-t':
    app.serial_timeout = int(value)
  elif key == '-r':
    app.iotools.force_raw_mode = True
  elif key == '-l':
    app.iotools.force_prg_mode = True
  elif key == '-v':
    app.verbose = True
  elif key == '-b':
    app.block_size,valid = app.iotools.parse_number(value)
  elif key == '-i':
    app.ignore_state = True
  elif key == '-f':
    app.force_old = True



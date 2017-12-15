#
# bootstrap.py - handle automatic bootstrapping
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
from dtv2ser.command import Command
from dtv2ser.status  import *
from dtv2sertool.iotools import IOTools

class Bootstrap:
  """Handle automatic bootstrap procedure to boot a DTV into basic or
     dtvtrans. This will upload files from TLR's dtvtrans distribution."""

  def __init__(self,dtvcmd,fast,screen_code,check_files):
    """Setup boostrap with command object"""
    self.dtvcmd      = dtvcmd
    self.fast        = fast
    self.screen_code = screen_code
    self.check_files = check_files
    self.iotools     = IOTools()

    self.first_wait   = 20
    self.wiggle_delay = 20
    self.prompt_delay = 12

    self.boot_txt_name     = "boot.txt"
    if screen_code:
      self.mlboot_prg_name = "mlboot_0400_joy2.prg"
      if fast:
        self.init_txt_name = "fast-sc.txt"
      else:
        self.init_txt_name = "init-sc.txt"
    else:
      self.mlboot_prg_name = "mlboot_joy2.prg"
      if fast:
        self.init_txt_name = "fast.txt"
      else:
        self.init_txt_name = ""
    self.dtvtrans_prg_name = "dtvtrans_joy2.prg"

    self.have_boot_txt     = False
    self.have_mlboot_prg   = False
    self.have_dtvtrans_prg = False
    self.have_init_txt     = False

  def load_boot_txt(self):
    """Load the boot.txt file and make sure it has a trailing RUN
       Returns status,data."""
    path = self.iotools.find_dist_file(self.boot_txt_name,"contrib")
    if path == '':
      return CLIENT_ERROR_FILE_ERROR,""
    status,data,start,is_prg = self.iotools.read_file(path)
    if status!=STATUS_OK or not self.check_files:
      return status,data

    # append RUN if its missing
    if not data.endswith("RUN\n"):
      data += "RUN\n"
      print "\tadded RUN"

    # fix port
    pos = data.find("56321")
    if pos != -1:
      print "\tfixing port 56321 -> 56320"
      data = data.replace("56321","56320");

    print "\t%d bytes basic boot code" % len(data)
    return STATUS_OK,data

  def load_init_txt(self):
    """Load the fast.txt file"""
    path = self.iotools.find_dist_file(self.init_txt_name,"bootstrap")
    if path == '':
      return CLIENT_ERROR_FILE_ERROR,""
    status,data,start,is_prg = self.iotools.read_file(path)
    if status!=STATUS_OK or not self.check_files:
      return status,data

    print "\t%d bytes basic init code" % len(data)
    return STATUS_OK,data

  def load_mlboot_prg(self):
    """Load mlboot.prg and patch it to be running automatically
       Returns status,data,start."""
    path = self.iotools.find_dist_file(self.mlboot_prg_name,"contrib")
    if path == '':
      return CLIENT_ERROR_FILE_ERROR,""
    status,data,start,is_prg = self.iotools.read_file(path)
    if status!=STATUS_OK or not self.check_files:
      return status,data,0

    # search for MLBOOT tag
    tag = "MLBOOT"
    taglen = len(tag)
    pos = data.find(tag)
    if pos == -1:
      print "\tno 'MLBOOT' tag found!!"
      return CLIENT_ERROR_FILE_ERROR,"",0

    # get parameters
    off = pos+taglen
    version_maj = ord(data[off])
    version_min = ord(data[off+1])
    port    = ord(data[off+2])
    autorun = ord(data[off+3])
    print "\tversion=%d.%d  port=0x%02x  autorun=0x%02x" % (version_maj,version_min,port,autorun)

    # check version
    if version_maj < 1:
      print "\tmlboot is too old. use version >= 1.0!"
      return CLIENT_ERROR_FILE_ERROR,"",0

    # check port
    if port != 0xfe:
      print "\tmlboot is not configured for joystick port 2!"
      return CLIENT_ERROR_FILE_ERROR,"",0

    # set autorun flag
    if autorun == 0:
      print "\tsetting autorun flag @",off+2
      data = data[0:off+3] + chr(1) + data[off+4:]

    # check for screen code
    if self.screen_code and start != 0x400:
      print "\tmlboot ist not located at 0x400!"
      return CLIENT_ERROR_FILE_ERROR,"",0

    print "\t%d bytes assembly boot code" % len(data)
    return STATUS_OK,data,start

  def load_dtvtrans_prg(self):
    """Load dtvtrans.prg and patch it to be running automatically
       Returns status,data,start."""
    path = self.iotools.find_dist_file(self.dtvtrans_prg_name,"contrib")
    if path == '':
      return CLIENT_ERROR_FILE_ERROR,""
    status,data,start,is_prg = self.iotools.read_file(path)
    if status!=STATUS_OK or not self.check_files:
      return status,data,0

    # search for - DTVTRANS / TLR -
    tag = "- DTVTRANS / TLR -"
    taglen = len(tag)
    pos = data.find(tag)
    if pos == -1:
      print "\tno '- DTVTRANS / TLR -' tag found!!"
      return CLIENT_ERROR_FILE_ERROR,"",0

    # get parameters
    off = pos+taglen
    version_maj = ord(data[off])
    version_min = ord(data[off+1])
    port = ord(data[off+8])
    bank = ord(data[off+9])
    autorun = ord(data[off+10])
    print "\tversion=%d.%d  port=0x%02x  bank=0x%02x  autorun=0x%02x" % (version_maj,version_min,port,bank,autorun)

    # check port
    if port != 0xfe:
      print "\tdtvtrans is not configured for joystick port 2!"
      return CLIENT_ERROR_FILE_ERROR,"",0

    # check version
    if version_maj < 1:
      print "\tdtvtrans is too old. use version >= 1.0!"
      return CLIENT_ERROR_FILE_ERROR,"",0

    # get load address

    # patch autorun
    if autorun == 0:
      print "\tsetting autorun flag @",off+10
      data = data[0:off+10] + chr(1) + data[off+11:]

    print "\t%d bytes dtvtrans code" % len(data)
    return STATUS_OK,data,start

  def load_boot_files(self):
    """Load all required boot files
       Returns status."""

    need_boot = not self.screen_code
    need_init = self.init_txt_name != ""
    need_mlboot = True

    # load boot.txt
    if need_boot and not self.have_boot_txt:
      status,self.boot_txt = self.load_boot_txt()
      if status != STATUS_OK:
        return status
      self.have_boot_txt = True

    # load fast.txt
    if need_init and not self.have_init_txt:
      status,self.init_txt = self.load_init_txt()
      if status != STATUS_OK:
        return status
      self.have_init_txt = True

    # load mlboot.prg
    if need_mlboot and not self.have_mlboot_prg:
      status,self.mlboot_prg,self.mlboot_start = self.load_mlboot_prg()
      if status != STATUS_OK:
        return status
      self.have_mlboot_prg = True

    return STATUS_OK

  def load_dtvtrans(self):
    # load dtvtrans.prg
    if not self.have_dtvtrans_prg:
      status,self.dtvtrans_prg,self.dtvtrans_start = self.load_dtvtrans_prg()
      if status != STATUS_OK:
        return status
      self.have_dtvtrans_prg = True

    return STATUS_OK

  # ---------- bootstrap modes ----------------------------------------------

  def bootstrap_basic(self):
    """Bootstrap a DTV into basic
       Returns status."""
    print "bootstrapping into basic"
    start_time = time.time()

    print "  resetting DTV"
    result = self.dtvcmd.dtv_reset(RESET_BYPASS_DTVMON)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return result

    print "  waiting %d seconds for slide show" % self.first_wait
    time.sleep(self.first_wait)

    print "  wiggling joystick for %d seconds to enter '$' mode" % self.wiggle_delay
    result,duration = self.dtvcmd.joy_wiggle(self.wiggle_delay,10,callback=self.iotools.print_size_dec)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return result
    self.iotools.print_duration(duration)

    print "  selecting basic prompt"
    result,duration = self.dtvcmd.joy_stream("8uf",joy_delay=15,callback=self.iotools.print_size_dec)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return result
    self.iotools.print_duration(duration)

    print "  waiting %d seconds for basic prompt" % self.prompt_delay
    time.sleep(self.prompt_delay)

    end_time = time.time()
    delta = end_time - start_time
    print "  booted basic in",self.iotools.time_string(delta)
    return STATUS_OK

  def bootstrap_boot(self):
    """Bootstrap from basic prompt into running boot code.
       Returns status."""
    need_init = self.init_txt_name != ""
    result = self.load_boot_files()
    if result != STATUS_OK:
      return result

    print "booting from basic"
    start_time = time.time()

    if self.have_init_txt:
      print "  typing init code from '%s'" % (self.init_txt_name)
      result,duration = self.dtvcmd.joy_type(self.init_txt,
                                             callback=self.iotools.print_size_dec)
      self.iotools.print_result(result)
      if result != STATUS_OK:
        return result
      self.iotools.print_duration(duration)

    if self.screen_code:
      boot_data = self.mlboot_prg
      boot_file = self.mlboot_prg_name
    else:
      boot_data = self.boot_txt
      boot_file = self.boot_txt_name
    print "  typing boot code from '%s'" % boot_file
    result,duration = self.dtvcmd.joy_type(boot_data,
                                           screen_code=self.screen_code,
                                           callback=self.iotools.print_size_dec)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return result
    self.iotools.print_duration(duration)

    time.sleep(0.5)

    if not self.screen_code:
      print "  sending %d bytes of mlboot assembly code" % len(self.mlboot_prg)
      result,stat = self.dtvcmd.write_boot_memory(self.mlboot_start,self.mlboot_prg,callback=self.iotools.print_size_dec)
      self.iotools.print_transfer_result(result,stat)
      if result != STATUS_OK:
        return result

      time.sleep(0.5)

    end_time = time.time()
    delta = end_time - start_time
    print "  booted initial stage in",self.iotools.time_string(delta)
    return STATUS_OK

  def bootstrap_dtvtrans(self,check=True):
    """Bootstrap from running basic boot into dtvtrans."""
    result = self.load_dtvtrans()
    if result != STATUS_OK:
      return result

    print "bootstrapping dtvtrans from initial boot stage"
    start_time = time.time()

    print "  sending 0x%04x bytes dtvtrans assembly code" % len(self.dtvtrans_prg)
    result,stat = self.dtvcmd.write_boot_memory(self.dtvtrans_start,self.dtvtrans_prg,callback=self.iotools.print_size)
    self.iotools.print_transfer_result(result,stat)
    if result != STATUS_OK:
      return result

    end_time = time.time()
    delta = end_time - start_time
    print "  booted dtvtrans in",self.iotools.time_string(delta)
    return STATUS_OK

  def bootstrap_full(self,screen_code=False,fast=False,check=True):
    """Bootstrap a DTV into dtvtrans
       Returns status."""

    start_time = time.time()

    # preload all required files
    status = self.load_boot_files()
    if status != STATUS_OK:
      return status
    status = self.load_dtvtrans()
    if status != STATUS_OK:
      return status

    # enter basic
    status = self.bootstrap_basic()
    if status != STATUS_OK:
      return status

    # boot initial stage
    status = self.bootstrap_boot()
    if status != STATUS_OK:
      return status

    # boot dtvtrans.prg
    status = self.bootstrap_dtvtrans()
    if status != STATUS_OK:
      return status

    end_time = time.time()
    duration = end_time - start_time
    print "  full bootstrap in",self.iotools.time_string(duration)

    return STATUS_OK
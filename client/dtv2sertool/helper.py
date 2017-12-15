#
# helper.py - helper operations for a all classes
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

class Helper:

  def __init__(self,dtvcmd,iotools,verbose,block_size):
    """create a new helper"""
    self.dtvcmd  = dtvcmd
    self.iotools = iotools
    self.verbose = verbose
    self.block_size = block_size

  def load_servlet(self,prg_name,prg_addr,verbose):
    """load a servlet program into dtv memory"""
    # get servlet file name
    file_name = self.iotools.find_dist_file(prg_name,"servlet")
    if file_name == "":
      return False

    # load servlet
    if verbose:
      print "  loading servlet '%s'" % file_name
    (result,data,start,is_prg) = self.iotools.read_file(file_name,verbose=False)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    if start != prg_addr:
      print "Servlet '%s' has invalid start address (expected 0x%04x)!" % (start,prg_addr)
      return False

    # upload servlet
    (result,stat) = self.dtvcmd.write_memory(0,start,data,
                                             callback=self.iotools.print_size,
                                             block_size=self.block_size)
    self.iotools.print_result(result)
    if result == STATUS_OK:
      return True
    else:
      return False

  def load_and_run_dtvtrans_ram(self):
    """Setup correct dtvtrans version for flash operations
       Returns True if all ok
    """
    print "  resetting..."
    result = self.dtvcmd.dtv_reset(RESET_ENTER_DTVTRANS)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False

    print "  is alive?"
    result = self.dtvcmd.is_alive()
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False

    print "  initializing BASIC"
    result = self.dtvcmd.init(INIT_FULL_BASIC)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False

    print "  query dtvtrans server"
    (result,port,mode,start,end) = self.dtvcmd.query_config()
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    if mode == 0:
      print "  dtvtrans already in RAM. OK!"
      return True

    print "  dtvtrans running in ROM. loading RAM version"

    # find dtvtrans.prg
    dtvtrans_name = "dtvtrans_joy%d.prg" % (port+1)
    path = self.iotools.find_dist_file(dtvtrans_name,"contrib")
    if path == '':
      return False

    (result,data,start,is_prg) = self.iotools.read_file(path)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    self.iotools.print_range(start,len(data))
    print "  sending program to DTV"
    result,stat = self.dtvcmd.write_memory(0,start,data,callback=self.iotools.print_size)
    self.iotools.print_transfer_result(result,stat)
    if result != STATUS_OK:
      return False

    # write BASIC range
    end = start + len(data)
    result = self.dtvcmd.write_word(0xae,end)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    result = self.dtvcmd.write_word(0x2d,end)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    result = self.dtvcmd.write_byte(0xba,8)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False

    # run BASIC
    print "  run program"
    result = self.dtvcmd.run()
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False

    # let dtvtrans run
    time.sleep(2)

    # reset into new version
    result = self.dtvcmd.dtv_reset(RESET_BYPASS_DTVMON)
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False

    print "  query dtvtrans server"
    (result,port,mode,start,end) = self.dtvcmd.query_config()
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    if mode != 0:
      print "  dtvtrans still in ROM. FAILED!"
      return False

    print "  dtvtrans is now in RAM. Good!"
    (result,impl) = self.dtvcmd.query_implementation()
    self.iotools.print_result(result)
    if result != STATUS_OK:
      return False

    print "    implementation: %s" % impl
    return True

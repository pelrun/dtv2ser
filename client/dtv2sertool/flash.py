#
# flash.py - flash operations
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

import sys

from dtv2ser.status  import *
from dtv2sertool.app import app

class Flash:

  # flash
  flash_size  = 0x200000
  sector_size = 0x010000
  high_area_size = 0x8000

  # flash_srv.prg:
  servlet_start  = 0x1000
  servlet_iobuf  = 0x2000
  servlet_rambuf = 0x20000

  # jumptable
  servlet_ident_flash   = 0x1000
  servlet_gen_map       = 0x1003
  servlet_program_flash = 0x1006

  # program flash mode (in acc)
  servlet_mode_erase        = 0
  servlet_mode_program      = 1
  servlet_mode_verify       = 2
  servlet_mode_check_empty  = 3

  servlet_error = (
    "OK",
    "Write Protected",
    "Verify Error",
    "Program Error",
    "Impossible",
    "Erase Error",
    "Lockdown",
    "Out of Range",
    "Auto Prog"
  )

  def __init__(self):
    self.loaded_servlet = False

  # ----- Tools -----

  def load_servlet(self):
    """Load the flash_srv.prg servlet"""
    if self.loaded_servlet:
      return True
    self.loaded_servlet = app.helper.load_servlet("flash_srv.prg",self.servlet_start,app.verbose)
    return self.loaded_servlet

  def download_range_pointers(self,start,length):
    """Download pointers to servlet_iobuf in DTV memory"""
    end = start + length
    if app.verbose:
      print "  downloading range pointers: start=0x%06x end=0x%06x" % (start,end)
    data =chr(start & 0xff)
    data+=chr((start >> 8) & 0xff)
    data+=chr((start >> 16) & 0xff)
    data+=chr(end & 0xff)
    data+=chr((end >> 8) & 0xff)
    data+=chr((end >> 16) & 0xff)
    result,stat = app.dtvcmd.write_memory(0,self.servlet_iobuf,data,
                                          callback=app.iotools.print_size,
                                          block_size=app.block_size)
    app.iotools.print_result(result)
    return result

  def print_dump_header(self,desc):
    print "          flash ROM map (%s)" % desc
    print "          0xxx 1xxx 2xxx 3xxx 4xxx 5xxx 6xxx 7xxx 8xxx 9xxx Axxx Bxxx Cxxx Dxxx Exxx Fxxx"

  def print_dump_line(self,addr,data):
    line = "  %06x: " % addr
    off  = 0
    size = len(data)
    while off < size:
      mem = data[off:off+4]
      off += 4
      line += mem + ' '
    print line

  def print_dump(self,data):
    off=0
    addr=0
    while addr < self.flash_size:
      line_data = data[off:off+64]
      self.print_dump_line(addr,line_data)
      off += 64
      addr += self.sector_size

  def check_range(self,start,length,wp,high_prot):
    # check range
    if start < self.sector_size and wp:
      print "ERROR: can't erase in first sector with write protection on!"
      return False
    end = start + length
    if end > self.flash_size:
      print "ERROR: range too large!"
      return False
    if high_prot and end > self.flash_size - self.high_area_size:
      print "ERROR: range inside protected high area!"
      return False
    return True

  def call_erase(self,do_it):
    # run servlet
    if not do_it:
      mode = self.servlet_mode_check_empty
    else:
      mode = self.servlet_mode_erase
    (result,sr,acc,xr,yr,duration) = app.dtvcmd.sys_call(self.servlet_program_flash,
                                                         acc=mode,timeout=60)
    app.iotools.print_result(result)
    app.iotools.print_duration(duration)
    if result != STATUS_OK:
      return False

    # check result
    if acc >= len(self.servlet_error):
      print "    result: invalid: (%02x)" % acc
      return False
    print "    result: %s" % self.servlet_error[acc]
    return acc == 0

  def call_program(self,do_it,verbose=True):
    # run servlet
    if not do_it:
      mode = self.servlet_mode_check_empty
    else:
      mode = self.servlet_mode_program
    (result,sr,acc,xr,yr,duration) = app.dtvcmd.sys_call(self.servlet_program_flash,
                                                         acc=mode,timeout=60)
    app.iotools.print_result(result)
    if verbose:
      app.iotools.print_duration(duration)
    if result != STATUS_OK:
      return False

    # check result
    if acc >= len(self.servlet_error):
      print "    result: invalid: %02x" % acc
      return False
    if acc != 0 or verbose:
      print "    result: %s" % self.servlet_error[acc]
    else:
      self.message("  result: ok",False)
    return acc == 0

  def call_verify(self,verbose=True):
    mode = self.servlet_mode_verify
    (result,sr,acc,xr,yr,duration) = app.dtvcmd.sys_call(self.servlet_program_flash,
                                                         acc=mode,timeout=30)
    app.iotools.print_result(result)
    if verbose:
      app.iotools.print_duration(duration)
    if result != STATUS_OK:
      return False

    # check result
    if acc >= len(self.servlet_error):
      print "    result: invalid: %02x" % acc
      return False
    if acc != 0 or verbose:
      print "    result: %s" % self.servlet_error[acc]
    else:
      self.message("  result: ok",False)
    return acc == 0

  def call_check_empty(self):
    """Check if ROM area is empty
    Returns ok
    """

    mode = self.servlet_mode_check_empty
    (result,sr,acc,xr,yr,duration) = app.dtvcmd.sys_call(self.servlet_program_flash,
                                                         acc=mode,timeout=10)
    app.iotools.print_result(result)
    app.iotools.print_duration(duration)
    if result != STATUS_OK:
      return False,False

    # check result
    if acc >= len(self.servlet_error):
      print "    result: invalid: %02x" % acc
      return False,False
    print "    result: %s" % self.servlet_error[acc]
    if acc == 0:
      empty = xr == 0xff
      print "    empty: ",empty
      return True,empty
    else:
      return False,False

  def compare_blocks(self,rom_sector,file_sector,width=1024):
    """Compare rom sector and file sector and decide what to do.
       Returns flash_begin,flash_end,line"""
    begin = -1
    end   = -1
    line = ""
    size = len(rom_sector)
    blks = size / width
    for x in xrange(blks):
      off = x * width
      erase_here = False
      flash_here = False
      for y in xrange(width):
        addr = off+y
        rom_data  = ord(rom_sector[addr])
        file_data = ord(file_sector[addr])
        if(rom_data != file_data):
          flash_here = True
        if((~rom_data) & file_data):
          erase_here = True
      if erase_here:
        line += "#"
      elif flash_here:
        line += "*"
      else:
        line += "."
      if erase_here or flash_here:
        if begin == -1:
          begin = off
        end = off + width
    return begin,end,line

  def message(self,msg,verbose):
    if verbose or app.verbose:
      print msg
    else:
      print " " * 40 + "\r",
      print msg + "\r",
      sys.stdout.flush()

  # ----- Flash Functions ---------------------------------------------------

  def do_ident_flash(self):
    """Call the ident flash function"""
    if not app.require_dtvtrans_10():
      return False,""

    # load servlet
    if not self.load_servlet():
      return False,""

    # run servlet
    (result,sr,acc,xr,yr,duration) = app.dtvcmd.sys_call(self.servlet_ident_flash)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False,""

    # map accu
    flash_names = ["NOT FOUND!","UNKNOWN",
                   "AT4XBV16X","AT4XBV16XT",
                   "SST39VF1681","SST39VF1682"]
    if acc >= len(flash_names):
      return False,""
    return True,flash_names[acc]


  def do_gen_map(self):
    """Generate a map of the flash"""
    if not app.require_dtvtrans_10():
      return False,None

    # load servlet
    if not self.load_servlet():
      return False,None

    # run servlet
    print "  generating flash map on DTV"
    (result,sr,acc,xr,yr,duration) = app.dtvcmd.sys_call(self.servlet_gen_map,timeout=30)
    app.iotools.print_result(result)
    app.iotools.print_duration(duration)
    if result != STATUS_OK:
      return False,None

    # read result
    if app.verbose:
      print "  downloading flash map"
    result,data,stat = app.dtvcmd.read_memory(0,self.servlet_iobuf,0x800,
                                              callback=app.iotools.print_size,
                                              block_size=app.block_size)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False,None

    # ok!
    return True,data


  def do_check(self,start,length):
    """Check if given ROM range is empty"""
    if not app.require_dtvtrans_10_in_ram():
      return False

    # load servlet
    if not self.load_servlet():
      return False

    # setup pointers: @0x2000
    status = self.download_range_pointers(start,length)
    if status != STATUS_OK:
      return False

    print "  checking flash range:"
    app.iotools.print_range(start,length,verbose=True)
    ok,empty = self.call_check_empty()
    return ok


  def do_erase(self,start,length,do_it,wp,verify,high_prot):
    """Perform a flash erase operation by calling the servlet on the DTV
       Returns True if all ok
    """
    if not app.require_dtvtrans_10_in_ram():
      return False

    # check range
    if not self.check_range(start,length,wp,high_prot):
      return False

    # load servlet
    if not self.load_servlet():
      return False

    # setup pointers: @0x2000
    status = self.download_range_pointers(start,length)
    if status != STATUS_OK:
      return False

    print "  erasing flash range: (%s)" % (("fake","REAL")[do_it])
    app.iotools.print_range(start,length,verbose=True)

    ok = self.call_erase(do_it)
    if not ok:
      return False

    if verify:
      print "  verifying flash range:"
      ok,empty = self.call_check_empty()
      return (ok and empty) or not do_it
    else:
      return True


  def do_verify(self,start,data,wp,high_prot):
    """Compare a data with flash contents by using the servlet verify
       Returns True if all ok
    """
    if not app.require_dtvtrans_10_in_ram():
      return False

    # check range
    length = len(data)
    if not self.check_range(start,length,wp,high_prot):
      return False

    # load servlet
    if not self.load_servlet():
      return False

    # setup pointers: @0x2000
    status = self.download_range_pointers(start,length)
    if status != STATUS_OK:
      return False

    # downloading data
    if app.verbose:
      print "  downloading data @0x%06x size 0x%06x" % (self.servlet_rambuf,len(data))
    result,stat = app.dtvcmd.write_memory(0,self.servlet_rambuf,data,
                                          callback=app.iotools.print_size,
                                          block_size=app.block_size)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False

    # do program
    print "  verifying flash range:"
    app.iotools.print_range(start,length,verbose=True)

    return self.call_verify()


  def do_program(self,start,data,do_it,wp,verify,high_prot,verbose=True):
    """Perform a flash program operation by calling the servlet on the DTV
       Returns True if all ok
    """
    if not app.require_dtvtrans_10_in_ram():
      return False

    # check range
    length = len(data)
    if not self.check_range(start,length,wp,high_prot):
      return False

    # load servlet
    if not self.load_servlet():
      return False

    # setup pointers: @0x2000
    status = self.download_range_pointers(start,length)
    if status != STATUS_OK:
      return False

    # downloading data
    if app.verbose:
      print "  downloading data @0x%06x size 0x%06x" % (self.servlet_rambuf,len(data))
    result,stat = app.dtvcmd.write_memory(0,self.servlet_rambuf,data,
                                          callback=app.iotools.print_size,
                                          block_size=app.block_size)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False

    # do program
    self.message("  programming flash range: (%s)" % (("fake","REAL")[do_it]),verbose)
    app.iotools.print_range(start,length,verbose=verbose)

    ok = self.call_program(do_it,verbose=verbose)
    if not ok:
      return False

    # do verify
    if verify:
      self.message("  verifying flash range:",verbose)
      ok = self.call_verify(verbose=verbose)
      return ok or not do_it
    else:
      return True


  def do_compare(self,file_data):
    """Compare the contents of a file with the flash"""
    # make sure its a ROM file
    if len(file_data) != self.flash_size:
      print "ERROR: no ROM file! (size is 0x%06x but 0x%06x expected)" % (len(file_data),self.flash_size)
      return False

    # sync main loop
    print "  comparing flash ROM"
    self.print_dump_header("'*'=flash '#'=erase+flash")
    addr = 0
    while(addr < self.flash_size):
      # read sector data
      result,rom_sector,stat = app.dtvcmd.read_memory(1,addr,self.sector_size,
                                                     callback=app.iotools.print_size,
                                                     block_size=app.block_size)
      if result != STATUS_OK:
        app.iotools.print_result(result)
        return False

      # analyze blocks
      file_sector = file_data[addr:addr+self.sector_size]
      begin,end,line = self.compare_blocks(rom_sector,file_sector)
      self.print_dump_line(addr,line)

      addr += self.sector_size

    return True


  def do_sync(self,file_data,do_it,wp,verify,high_prot,start_addr,end_addr_opt,sync_all):
    """Perform a flash sync operation by calling the servlet on the DTV
       Returns True if all ok
    """
    if not app.require_dtvtrans_10_in_ram():
      return False

    # make sure its a ROM file
    if len(file_data) != self.flash_size:
      print "ERROR: no ROM file! (size is 0x%06x but 0x%06x expected)" % (len(file_data),self.flash_size)
      return False

    # sync main loop
    print "  syncing flash ROM"
    self.print_dump_header("'*'=flash '#'=erase+flash")

    if start_addr != -1:
      addr = start_addr
    elif wp:
      addr = self.sector_size
    else:
      addr = 0

    if end_addr_opt != -1:
      end_addr = end_addr_opt
    if high_prot:
      end_addr = self.flash_size - self.high_area_size
    else:
      end_addr = self.flash_size

    while(addr < end_addr):
      segment_size = end_addr - addr
      if segment_size > self.sector_size:
        segment_size = self.sector_size

      # read sector data
      result,rom_sector,stat = app.dtvcmd.read_memory(1,addr,segment_size,
                                                      callback=app.iotools.print_size,
                                                      block_size=app.block_size)
      if result != STATUS_OK:
        app.iotools.print_result(result)
        return False

      # analyze blocks
      file_sector = file_data[addr:addr+segment_size]
      begin,end,line = self.compare_blocks(rom_sector,file_sector)
      self.print_dump_line(addr,line)

      # sync all overwrite
      if sync_all:
        begin  = 0
        end    = self.sector_size

      # have something to flash here
      if begin != -1:
        rom_begin = addr + begin
        length    = end - begin

        # download data to RAM buffer
        file_burn_data = file_sector[begin:end]

        # flash range
        if not self.do_program(rom_begin,file_burn_data,do_it,wp,verify,high_prot,verbose=False):
          return False

      addr += self.sector_size

    return True


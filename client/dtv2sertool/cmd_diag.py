#
# cmd_diag.py - diagnose commands to test the dtv2ser device
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

import random

from dtv2ser.status  import *
from dtv2sertool.cmd import Cmd
from dtv2sertool.app import app

# ----- Tools -----

def diag_parse_pattern(args):
  if len(args)==2:
    pattern,valid = app.iotools.parse_number(args[1])
    if not valid:
      return None
  else:
    pattern = 0xff
  return pattern

def diag_parse_size_pattern(args):
  pattern = diag_parse_pattern(args)
  if pattern == None:
    return None,None
  size,valid = app.iotools.parse_number(args[0])
  if not valid:
    return None,None
  return size,pattern

def diag_parse_range_pattern(args):
  pattern = diag_parse_pattern(args)
  if pattern == None:
    return None,None
  r,valid = app.iotools.parse_range(args[0])
  if not valid:
    return None,None
  return r,pattern

# ----- Commands -----

def diag_read_only_client(cmd,args,opts):
  if not app.require_server_alive():
    return False

  size,pattern = diag_parse_size_pattern(args)
  if size == None:
    return False
  print "  * reading 0x%06x pattern bytes (0x%02x) from dtv2ser device via serial" % (size,pattern)
  (result,stat) = app.dtvcmd.diagnose_read_memory_only_client(size,
                                                              callback=app.iotools.print_size,
                                                              pattern=pattern,
                                                              block_size=app.block_size)
  app.iotools.print_transfer_result(result,stat)
  return result == STATUS_OK

def diag_write_only_client(cmd,args,opts):
  if not app.require_server_alive():
    return False

  size,pattern = diag_parse_size_pattern(args)
  if size == None:
    return False
  print "  * writing 0x%06x pattern bytes (0x%02x) to dtv2ser device via serial" % (size,pattern)
  (result,stat) = app.dtvcmd.diagnose_write_memory_only_client(size,
                                                               callback=app.iotools.print_size,
                                                               pattern=pattern,
                                                               block_size=app.block_size)
  app.iotools.print_transfer_result(result,stat)
  return result == STATUS_OK

def diag_read_only_dtv(cmd,args,opts):
  if not app.require_server_alive():
    return False

  (rom,start,length,valid) = app.iotools.parse_range(args[0])
  pattern = diag_parse_pattern(args)
  if pattern == None:
    return False
  print "  * reading 0x%06x pattern bytes (0x%02x) from DTV to dtv2ser device only" % (length,pattern)
  app.iotools.print_range(start,length)
  (result,stat) = app.dtvcmd.diagnose_read_memory_only_dtv(rom,start,length,
                                                           callback=app.iotools.print_size,
                                                           pattern=pattern,
                                                           block_size=app.block_size)
  app.iotools.print_transfer_result(result,stat)
  return result == STATUS_OK

def diag_write_only_dtv(cmd,args,opts):
  if not app.require_server_alive():
    return False

  (rom,start,length,valid) = app.iotools.parse_range(args[0])
  pattern = diag_parse_pattern(args)
  if pattern == None:
    return False
  print "  * writing 0x%06x pattern bytes (0x%02x) from dtv2ser device to DTV only" % (length,pattern)
  app.iotools.print_range(start,length)
  (result,stat) = app.dtvcmd.diagnose_write_memory_only_dtv(rom,start,length,
                                                            callback=app.iotools.print_size,
                                                            pattern=pattern,
                                                            block_size=app.block_size)
  app.iotools.print_transfer_result(result,stat)
  return result == STATUS_OK

def diag_read(cmd,args,opts):
  if not app.require_server_alive():
    return False

  (rom,start,size,valid) = app.iotools.parse_range(args[0])
  pattern = diag_parse_pattern(args)
  if pattern == None:
    return False
  print "  * dummy read 0x%06x pattern bytes (0x%02x) from DTV" % (size,pattern)
  (result,data,stat) = app.dtvcmd.read_memory(rom,start,size,
                                              callback=app.iotools.print_size,
                                              block_size=app.block_size)
  app.iotools.print_transfer_result(result,stat)
  if result != STATUS_OK:
    return False
  ref_data = chr(pattern) * size
  if ref_data != data:
    print "VERIFY MISMATCH!"
    return False
  return True

def diag_write(cmd,args,opts):
  if not app.require_server_alive():
    return False

  (rom,start,size,valid) = app.iotools.parse_range(args[0])
  pattern = diag_parse_pattern(args)
  if pattern == None:
    return False
  ref_data = chr(pattern) * size
  print "  * dummy write 0x%06x pattern bytes (0x%02x) to DTV" % (size,pattern)
  (result,stat) = app.dtvcmd.write_memory(rom,start,ref_data,
                                          callback=app.iotools.print_size,
                                          block_size=app.block_size)
  app.iotools.print_transfer_result(result,stat)
  return result == STATUS_OK

def diag_testsuite(cmd,args,opts):
  if not app.require_server_alive():
    return False

  test_range = ["0x20000,0x10000"]
  test_size  = ["0x10000"]
  if not diag_write_only_client("",test_size,[]):
    return False
  if not diag_read_only_client("",test_size,[]):
    return False
  if not diag_write_only_dtv("",test_range,[]):
    return False
  if not diag_read_only_dtv("",test_range,[]):
    return False
  if not diag_write("",test_range,[]):
    return False
  if not diag_read("",test_range,[]):
    return False
  print "  * ALL TESTS PASSED OK! *"
  return True

def diag_sys(cmd,args,opts):
  if not app.require_server_alive():
    return False

  # loading diagnose servlet
  if not app.helper.load_servlet("diag_srv.prg",0x1000,True):
    return False

  retries = 25
  if len(args)==1:
    retries,valid = app.iotools.parse_number(args[0])
    if not valid:
      return False

  # do sys call
  print "  testing %d sys calls with wait and return value fetch" % retries
  for i in xrange(retries):
    a = random.randint(1,255)
    print "  * %d/%d: testing sys call with %d frames duration" % (i,retries,a)
    (result,sr,acc,xr,yr,duration) = app.dtvcmd.sys_call(0x1000,
                                                         acc=a,timeout=60)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    app.iotools.print_duration(duration)
    if acc != 42 or xr != a or yr != 0:
      print "FAILED: wrong result!! acc=0x%02x xr=0x%02x yr=0x%02x" % (acc,xr,yr)
      return False
  print "  * %d/%d: all calls passed OK!" % (retries,retries)

  return True


def init(cmdSet):

  # param
  diagCmd = Cmd(["diag","diagnose"],
  help="diagnose commands")
  cmdSet.add_command(diagCmd)

  diagCmd.add_sub_command(Cmd(["testsuite"],
  help="test the dtv2ser device",
  func=diag_testsuite))

  diagCmd.add_sub_command(Cmd(["read"],
  help="receive test pattern from DTV via dtv2ser",
  opts=(1,2,"<range> [<pattern>]"),
  func=diag_read))

  diagCmd.add_sub_command(Cmd(["write"],
  help="write test pattern to DTV via dtv2ser",
  opts=(1,2,"<range> [<pattern>]"),
  func=diag_write))

  diagCmd.add_sub_command(Cmd(["read_only_client"],
  help="receive test pattern from dtv2ser",
  opts=(1,2,"<size> [<pattern>]"),
  func=diag_read_only_client))

  diagCmd.add_sub_command(Cmd(["write_only_client"],
  help="write test pattern to dtv2ser",
  opts=(1,2,"<size> [<pattern>]"),
  func=diag_write_only_client))

  diagCmd.add_sub_command(Cmd(["read_only_dtv"],
  help="receive test pattern from DTV (no client)",
  opts=(1,2,"<range> [<pattern>]"),
  func=diag_read_only_dtv))

  diagCmd.add_sub_command(Cmd(["write_only_dtv"],
  help="write test pattern to DTV (no client)",
  opts=(1,2,"<range> [<pattern>]"),
  func=diag_write_only_dtv))

  # fill command
  cmdSet.add_command(Cmd(["fill","f"],
  help='''fill memory of DTV''',
  opts=(1,2,'<range> [<pattern>]'),
  func=diag_write_only_dtv))

  # sys diagnode
  diagCmd.add_sub_command(Cmd(["sys"],
  help="test the sys command",
  opts=(0,1,'[retries]'),
  func=diag_sys))


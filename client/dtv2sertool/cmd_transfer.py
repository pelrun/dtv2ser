#
# cmd_transfer.py - transfer commands
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
from dtv2sertool.cmd import Cmd
from dtv2sertool.app import app

def read(cmd,args,opts):
  if not app.require_server_alive():
    return False

  # get range
  if len(args) == 2:
    (rom,start,length,valid) = app.iotools.parse_range(args[0])
  else:
    rom=0
    (result,start) = app.dtvcmd.read_word(0x2b)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    (result,end) = app.dtvcmd.read_word(0x2d)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    length = end - start

  # read data
  app.iotools.print_range(start,length)
  print "  receiving %s memory from DTV" % (('RAM','ROM')[rom])
  result,data,stat = app.dtvcmd.read_memory(rom,start,length,
                                            callback=app.iotools.print_size,
                                            block_size=app.block_size)
  app.iotools.print_transfer_result(result,stat)
  if result != STATUS_OK:
    return False

  # write file
  result,is_prg = app.iotools.write_file(args[-1],data,start)
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False
  return True


def write(cmd,args,opts):
  if not app.require_server_alive():
    return False

  # read file
  (result,data,start,is_prg) = app.iotools.read_file(args[-1])
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False

  # parse start
  rom=0
  if len(args) == 2:
    rom,start = app.iotools.parse_write_start(args[0])

  # write data
  app.iotools.print_range(start,len(data))
  print "  sending %s memory to DTV" % (('RAM','ROM')[rom])
  result,stat = app.dtvcmd.write_memory(rom,start,data,
                                        callback=app.iotools.print_size,
                                        block_size=app.block_size)
  app.iotools.print_transfer_result(result,stat)
  if result != STATUS_OK:
    return False
  return True


def verify(cmd,args,opts):
  if not app.require_server_alive():
    return False

  # read file
  rom = 0
  (result,verify_data,start,is_prg) = app.iotools.read_file(args[-1])
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False

  # get range
  if len(args) == 2:
    rom,start = app.iotools.parse_write_start(args[0])

  # read data
  length = len(verify_data)
  app.iotools.print_range(start,length)
  print "  receiving %s memory from DTV" % (('RAM','ROM')[rom])
  result,data,stat = app.dtvcmd.read_memory(rom,start,length,
                                            callback=app.iotools.print_size,
                                            block_size=app.block_size)
  app.iotools.print_transfer_result(result,stat)

  # verify data
  if result == STATUS_OK:
    if verify_data == data:
      print "  data:     verified ok"
      return True
    else:
      for i in xrange(len(data)):
        if data[i] != verify_data[i]:
          break
      print "  data:     verify MISMATCH! (@%06x: dtv=%02x file=%02x)" \
        % (i,ord(data[i]),ord(verify_data[i]))
      return False
  else:
    return False


def boot(cmd,args,opts):
  # read file
  (result,data,start,is_prg) = app.iotools.read_file(args[-1])
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False

  # parse start
  if len(args) == 2:
    rom,start = app.iotools.parse_write_start(args[0])

  # write data
  app.iotools.print_range(start,len(data))
  print "  sending boot file to DTV"
  result,stat = app.dtvcmd.write_boot_memory(start,data,
                                             callback=app.iotools.print_size)
  app.iotools.print_transfer_result(result,stat)
  if result != STATUS_OK:
    return False
  return True


def init(cmdSet):
  # read command
  cmdSet.add_command(Cmd(["read","rd","r"],
  help='''read memory from DTV
range: [[r]<start>,<length>]
       [[r]<start>-<end>]
prepend r for ROM, default: RAM''',
  opts=(1,2,'[<range>] <file>'),
  func=read))

  # verify command
  cmdSet.add_command(Cmd(["verify","vfy","v"],
  help='''verfiy memory from DTV against file
range: [[r]<start>,<length>]
       [[r]<start>-<end>]
prepend r for ROM, default: RAM''',
  opts=(2,2,'<range> <file>'),
  func=verify))

  # write command
  cmdSet.add_command(Cmd(["write","wr","w"],
  help='''write memory to DTV''',
  opts=(1,2,'[<address>] <file>'),
  func=write))

  # boot command
  cmdSet.add_command(Cmd(["boot","bt","b"],
  help='''send a program via the boot protocol''',
  opts=(1,2,'[<address>] <file>'),
  func=boot))


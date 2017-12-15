#
# cmd_flash.py - flash commands
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

from dtv2ser.status  import *
from dtv2sertool.flash import Flash
from dtv2sertool.cmd import Cmd
from dtv2sertool.app import app

# ----- Tools -----

def flash_parse_opts(opts):
  do_it = False
  wp = True
  verify = False
  high_prot = False
  for o in opts:
    if o[0] == '-f':
      do_it = True
    if o[0] == '-w':
      wp = False
    if o[0] == '-v':
      verify = True
    if o[0] == '-p':
      high_prot = True
  return do_it,wp,verify,high_prot

# ----- Command -----

def flash_map(cmd,args,opts):
  f = Flash()
  ok,data = f.do_gen_map()
  if not ok:
    return False

  f.print_dump_header("'.'=empty '*'=filled")
  f.print_dump(data)
  return True


def flash_identify(cmd,args,opts):
  f = Flash()
  ok,t = f.do_ident_flash()
  if not ok:
    return False
  print "  flash type: %s" % t
  return True


def flash_dump(cmd,args,opts):
  if not app.require_server_alive():
    return False

  file_name = args[-1]
  print "  dumping flash ROM to file '%s'" % file_name

  # read full ROM image
  result,data,stat = app.dtvcmd.read_memory(1,0,Flash.flash_size,
                                            callback=app.iotools.print_size,
                                            block_size=app.block_size)
  app.iotools.print_transfer_result(result,stat)
  if result != STATUS_OK:
    return False

  # write file
  result,is_prg = app.iotools.write_file(file_name,data,0)
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False
  return True


def flash_compare(cmd,args,opts):
  # read file
  file_name = args[-1]
  (result,file_data,start,is_prg) = app.iotools.read_file(file_name)
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False

  f=Flash()
  return f.do_compare(file_data)


def flash_sync(cmd,args,opts):
  if not app.require_dtvtrans_10():
    return False

  # parse optional start and end address
  start_addr = -1
  end_addr = -1
  sync_all = False
  for o in opts:
    if o[0] == '-s':
      start_addr,valid = app.iotools.parse_number(o[1])
      if not valid:
        print "ERROR: parsing start address: ",o[1]
        return False
    elif o[0] == '-e':
      end_addr,valid = app.iotools.parse_number(o[1])
      if not valid:
        print "ERROR: parsing end address: ",o[1]
        return False
    elif o[0] == '-a':
      sync_all = True

  # read file
  file_name = args[-1]
  (result,file_data,start,is_prg) = app.iotools.read_file(file_name)
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False

  # parse opts
  do_it,wp,verify,hp = flash_parse_opts(opts)

  f=Flash()
  return f.do_sync(file_data,do_it,wp,verify,hp,start_addr,end_addr,sync_all)


def flash_program(cmd,args,opts):
  if not app.require_dtvtrans_10():
    return False

  # read file
  rom = 0
  (result,data,start,is_prg) = app.iotools.read_file(args[1])
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False

  # parse range
  rom,start = app.iotools.parse_write_start(args[0])
  if rom == -1:
    print "ERROR: invalid start address given!"
    return False

  # parse opts
  do_it,wp,verify,hp = flash_parse_opts(opts)

  f=Flash()
  return f.do_program(start,data,do_it,wp,verify,hp)


def flash_erase(cmd,args,opts):
  # parse range
  rom,start,length,valid = app.iotools.parse_range(args[0])
  if not valid:
    print "ERROR: invalid range given!"
    return False

  # parse opts
  do_it,wp,verify,hp = flash_parse_opts(opts)

  f=Flash()
  return f.do_erase(start,length,do_it,wp,verify,hp)


def flash_verify(cmd,args,opts):
  if not app.require_dtvtrans_10():
    return False

  # read file
  rom = 0
  (result,data,start,is_prg) = app.iotools.read_file(args[1])
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False

  # parse range
  rom,start = app.iotools.parse_write_start(args[0])
  if rom == -1:
    print "ERROR: invalid start address given!"
    return False

  # parse opts
  do_it,wp,verify,hp = flash_parse_opts(opts)

  f=Flash()
  return f.do_verify(start,data,wp,hp)


def flash_check(cmd,args,opts):
  # parse range
  rom,start,length,valid = app.iotools.parse_range(args[0])
  if not valid:
    print "ERROR: invalid range given!"
    return False

  f=Flash()
  return f.do_check(start,length)


def init(cmdSet):
  # flash
  flashCmd = Cmd(["flash"],
  help="read/modify the flash ROM of the DTV")
  cmdSet.add_command(flashCmd)

  flashCmd.add_sub_command(Cmd(["map"],
  help="print a map of the ROM",
  func=flash_map))

  flashCmd.add_sub_command(Cmd(["identify","id"],
  help="identify flash type",
  func=flash_identify))

  flashCmd.add_sub_command(Cmd(["dump"],
  help="dump the contents of the ROM to a file",
  opts=(1,1,"<file>"),
  func=flash_dump))

  flashCmd.add_sub_command(Cmd(["compare"],
  help="compare the contents of the ROM to a file",
  opts=(1,1,"<file>"),
  func=flash_compare))

  flashCmd.add_sub_command(Cmd(["sync"],
  help="""sync the contents of a file to ROM.
WARNING: Only with -f set
this will erase/program parts of the ROM!!!""",
  opts=(1,1,"<file>"),
  args=[
    ('f',None,'really flash. otherwise pretend to do so.'),
    ('w',None,'remove write-protection of first sector.'),
    ('p',None,'protect high area at $1f8000'),
    ('v',None,'verify after flash'),
    ('s','<addr>','start address of range'),
    ('e','<addr>','end address of range'),
    ('a',None,'sync whole range not only differences')
  ],
  func=flash_sync))

  flashCmd.add_sub_command(Cmd(["program"],
  help="""program range of flash ROM
WARNING: Only with -f set
this will program parts of the ROM!!!""",
  opts=(2,2,"<start> <file>"),
  args=[
    ('f',None,'really flash. otherwise pretend to do so.'),
    ('w',None,'remove write-protection of first sector.'),
    ('p',None,'protect high area at $1f8000'),
    ('v',None,'verify after flash')
  ],
  func=flash_program))

  flashCmd.add_sub_command(Cmd(["erase"],
  help="""erase range of flash ROM
WARNING: Only with -f set
this will erase parts of the ROM!!!""",
  opts=(1,1,"<range>"),
  args=[
    ('f',None,'really flash. otherwise pretend to do so.'),
    ('w',None,'remove write-protection of first sector.'),
    ('p',None,'protect high area at $1f8000'),
    ('v',None,'verify after erase')
  ],
  func=flash_erase))

  flashCmd.add_sub_command(Cmd(["verify"],
  help="""verify contents of file with ROM contents
Use servlet code for that!""",
  opts=(2,2,"<start> <file>"),
  args=[
    ('w',None,'remove write-protection of first sector.'),
    ('p',None,'protect high area at $1f8000')
  ],
  func=flash_verify))

  flashCmd.add_sub_command(Cmd(["check"],
  help="""check if ROM range is empty""",
    opts=(1,1,"<range>"),
    func=flash_check))


#
# cmd_dtvtrans.py - dtvtrans commands
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
from dtv2ser.status import *
from dtv2sertool.cmd import Cmd
from dtv2sertool.app import app

def sys(cmd,args,opts):
  if not app.require_dtvtrans_10():
    return False

  timeout = 10.0
  acc = 0
  xr  = 0
  yr  = 0
  sr  = 0
  mem = 7
  for o,a in opts:
    if o == '-a':
      acc,v = app.iotools.parse_number(a)
    elif o == '-x':
      xr,v = app.iotools.parse_number(a)
    elif o == '-y':
      yr,v = app.iotools.parse_number(a)
    elif o == '-s':
      sr,v = app.iotools.parse_number(a)
    elif o == '-m':
      mem,v = app.iotools.parse_number(a)
    elif o == '-t':
      timeout,v = app.iotools.parse_number(a)

  addr,valid = app.iotools.parse_number(args[0])
  if not valid:
    return False

  print "  sys: calling code at 0x%04x" % addr
  print "    in:     SR=%s A=0x%02x X=0x%02x Y=0x%02x  MEM(0x01)=0x%02x" \
    % (app.iotools.status_reg_string(sr),acc,xr,yr,mem)
  (result,sr,acc,xr,yr,duration) = app.dtvcmd.sys_call(addr,sr=sr,acc=acc,xr=xr,yr=yr,iocfg=mem,timeout=timeout)
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False
  print "    out:    SR=%s A=0x%02x X=0x%02x Y=0x%02x" \
    % (app.iotools.status_reg_string(sr),acc,xr,yr)
  print "    time:   %s" % app.iotools.time_string(duration)
  return True


def reset(cmd,args,opts):
  reset_mode = RESET_ENTER_DTVTRANS
  init       = True
  init_mode  = INIT_FULL_BASIC
  for o,a in opts:
    if o == '-N':
      reset_mode = RESET_BYPASS_DTVMON
      init = False
    elif o == '-d':
      reset_mode = RESET_NORMAL
      init = False
    elif o == '-n':
      init = False
    elif o == '-B':
      mode = INIT_FULL_BASIC
    elif o == '-b':
      mode = INIT_MINIMAL_BASIC
    elif o == '-K':
      mode = INIT_FULL_KERNAL
    elif o == '-k':
      mode = INIT_MINIMAL_KERNAL

  print "  resetting dtv...",("normal","enter dtvtrans","bypass dtvmon")[reset_mode]
  result = app.dtvcmd.dtv_reset(reset_mode)
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False

  if init and app.has_dtvtrans_10():
    print "  initializing",init_mode_text[init_mode]
    result = app.dtvcmd.init(init_mode)
    app.iotools.print_result(result)
    if result == STATUS_OK and (init_mode==INIT_FULL_BASIC or init_mode==INIT_MINIMAL_BASIC):
      result = app.dtvcmd.do_print(string_init_screen)
      app.iotools.print_result(result)
    if result != STATUS_OK:
      return False
  return True


def dtvtrans_init(cmd,args,opts):
  if not app.require_dtvtrans_10():
    return False

  init_mode  = INIT_FULL_BASIC
  for o,a in opts:
    if o == '-B':
      init_mode = INIT_FULL_BASIC
    elif o == '-b':
      init_mode = INIT_MINIMAL_BASIC
    elif o == '-K':
      init_mode = INIT_FULL_KERNAL
    elif o == '-k':
      init_mode = INIT_MINIMAL_KERNAL
  print "  initializing",init_mode_text[init_mode]
  result = app.dtvcmd.init(init_mode)
  app.iotools.print_result(result)
  if result == STATUS_OK and (init_mode==INIT_FULL_BASIC or init_mode==INIT_MINIMAL_BASIC):
    result = app.dtvcmd.do_print(string_init_screen)
    app.iotools.print_result(result)
  return result == STATUS_OK


def load(cmd,args,opts):
  if not app.require_server_alive():
    return False

  simulate_load = True
  load_mode = LOAD_NORMAL
  for o,a in opts:
    if o == '-N':
      simulate_load = False
    elif o == '-n':
      load_mode = LOAD_NO_RELINK

  end = 0
  if len(args) == 1:
    name = args[-1]
    print "writing file '%s'" % name
    (result,data,start,is_prg) = app.iotools.read_file(name)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False

    if start != 0x801:
      print "ERROR: invalid start address! expected $0801!"
      return False

    app.iotools.print_range(start,len(data))
    print "  sending program to DTV"
    result,stat = app.dtvcmd.write_memory(0,start,data,callback=app.iotools.print_size)
    app.iotools.print_transfer_result(result,stat)
    if result != STATUS_OK:
      return False

    # write
    end = start + len(data)
    result = app.dtvcmd.write_word(0xae,end)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    result = app.dtvcmd.write_word(0x2d,end)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    result = app.dtvcmd.write_byte(0xba,8)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False
  else:
    # read start address
    result,start = app.dtvcmd.read_word(0x2b)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    # read end address
    result,end = app.dtvcmd.read_word(0x2d)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False

  # dtvtrans 1.0: simulate load
  if simulate_load and app.has_dtvtrans_10():
    print "  simulating load 0x%04x-0x%04x" % (start,end)
    result = app.dtvcmd.do_print(string_load)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False
    result = app.dtvcmd.load(load_mode)
    app.iotools.print_result(result)
    if result != STATUS_OK:
      return False
  return True


def save(cmd,args,opts):
  if not app.require_server_alive():
    return False

  result,start = app.dtvcmd.read_word(0x2b)
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False
  result,end = app.dtvcmd.read_word(0x2d)
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False
  print "  simulating save 0x%04x-0x%04x" % (start,end)

  # read data
  length = end - start
  app.iotools.print_range(start,length)
  print "  receiving memory from DTV"
  result,data,stat = app.dtvcmd.read_memory(0,start,length,callback=app.iotools.print_size)
  app.iotools.print_transfer_result(result,stat)
  if result != STATUS_OK:
    return False

  # write file
  result,is_prg = app.iotools.write_file(args[-1],data,start)
  app.iotools.print_result(result)

  # dtvtrans 1.0: print message
  if result == STATUS_OK and app.has_dtvtrans_10():
    result = app.dtvcmd.do_print(string_save)
    app.iotools.print_result(result)
  return result == STATUS_OK


def run(cmd,args,opts):
  if not app.require_dtvtrans_10():
    return False

  print "  executing BASIC RUN"
  result = app.dtvcmd.do_print(string_run)
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False
  result = app.dtvcmd.run()
  app.iotools.print_result(result)
  return result == STATUS_OK


def exit(cmd,args,opts):
  if not app.require_dtvtrans_10():
    return False

  exit_mode = EXIT_NORMAL
  for o,a in opts:
    if o == '-n':
      exit_mode = EXIT_ONLY_EXIT
  print "  exiting to BASIC"
  result = app.dtvcmd.do_print(string_no_cursor)
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False
  result = app.dtvcmd.exit(exit_mode)
  app.iotools.print_result(result)
  return result == STATUS_OK


def sleep(cmd,args,opts):
  num,valid = app.iotools.parse_number(args[0])
  if not valid:
    print "ERROR: sleep <sec>"
    return False
  time.sleep(num)
  return True


def init(cmdSet):
  # sys command
  cmdSet.add_command(Cmd(["sys","go","g"],
  help='''jump to memory location on DTV\nand wait for execution''',
  opts=(1,1,'<address>'),
  func=sys,
  args=[
    ('a','<byte>','set ACCU'),
    ('x','<byte>','set X register'),
    ('y','<byte>','set Y register'),
    ('s','<byte>','set status register'),
    ('m','<byte>','set memory config ($01)'),
    ('t','<seconds>','set timeout for execution')
  ]
  ))

  # reset command
  cmdSet.add_command(Cmd(["reset","x"],
  help='''reset DTV and enter dtvmon/dtvtrans''',
  func=reset,
  args=[
    ('N',None,'reset and bypass dtvmon)'),
    ('d',None,'normal reset and enter dtvmon'),
    ('n',None,'enter dtvtrans but no init'),
    ('B',None,'+ init full BASIC'),
    ('b',None,'+ init minimal BASIC'),
    ('K',None,'+ init full KERNAL'),
    ('k',None,'+ init minimal KERNAL')
  ]
  ))

  # init command
  cmdSet.add_command(Cmd(["init"],
  help='''initialize KERNAL and/or BASIC''',
  func=dtvtrans_init,
  args=[
    ('B',None,'+ init full BASIC'),
    ('b',None,'+ init minimal BASIC'),
    ('K',None,'+ init full KERNAL'),
    ('k',None,'+ init minimal KERNAL')
  ]
  ))

  # load command
  cmdSet.add_command(Cmd(["load"],
  help='''simulate a BASIC LOAD''',
  opts=(0,1,'[<file>]'),
  func=load,
  args=[
    ('N',None,'do not simulate'),
    ('n',None,'no relink only clr')
  ]
  ))

  # save command
  cmdSet.add_command(Cmd(["save"],
  help='''simulate a BASIC SAVE''',
  opts=(1,1,'<file>'),
  func=save))

  # run command
  cmdSet.add_command(Cmd(["run"],
  help='''execute a BASIC RUN''',
  func=run))

  # exit command
  cmdSet.add_command(Cmd(["exit"],
  help='''BASIC exit''',
  func=exit,
  args=[
    ('n',None,'only exit, no clr')
  ]
  ))

  # sleep command
  cmdSet.add_command(Cmd(["sleep"],
  help='''take a short nap''',
  opts=(1,1,'<seconds>'),
  func=sleep))



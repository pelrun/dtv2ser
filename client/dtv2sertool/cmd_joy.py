#
# cmd_joy.py - joystick/autotype commands
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
from dtv2sertool.cmd import Cmd
from dtv2sertool.app import app

# ----- Tools -----

def joy_get_optional_delay(pos,args,default_delay):
  delay = default_delay
  if pos < len(args):
    delay,valid = app.iotools.parse_number(args[pos])
    if not valid:
      return default_delay
  return delay

# ----- Commands -----

def joy_wiggle(cmd,args,opts):
  wiggle_time = int(args[0])
  delay = joy_get_optional_delay(1,args,10)
  result,duration = app.dtvcmd.joy_wiggle(wiggle_time,delay,callback=app.iotools.print_size_dec)
  app.iotools.print_result(result)
  if result == STATUS_OK:
    app.iotools.print_duration(duration)
    return True
  else:
    return False


def joy_rawkey(cmd,args,opts):
  x = int(args[0])
  y = int(args[1])
  delay = joy_get_optional_delay(2,args,6)
  result,duration = app.dtvcmd.joy_rawkey((x,y),delay,callback=app.iotools.print_size_dec)
  app.iotools.print_result(result)
  if result == STATUS_OK:
    app.iotools.print_duration(duration)
    return True
  else:
    return False


def joy_stream(cmd,args,opts):
  is_string = False
  joy_delay = 0
  verbose   = False
  test_mode = False
  for o,a in opts:
    if o == '-i':
      is_string = True
    elif o == '-j':
      joy_delay = int(a)
    elif o == '-v':
      verbose = True
    elif o == '-n':
      test_mode = True

  if is_string:
    data = args[0]
  else:
    result,data,start,is_prg = app.iotools.read_file(args[0])
    if result != STATUS_OK:
      app.iotools.print_result(result)
      return False
    if is_prg:
      print "ERROR: don't use a prg for a joy string!"
      return False

  result,duration = app.dtvcmd.joy_stream(data,joy_delay=joy_delay,
                                          verbose=verbose,test_mode=test_mode,
                                          callback=app.iotools.print_size_dec)
  app.iotools.print_result(result)
  if result == STATUS_OK:
    app.iotools.print_duration(duration)
    return True
  else:
    return False


def joy_type(cmd,args,opts):
  is_string   = False
  screen_code = False
  type_delay  = 0
  joy_delay   = 0
  start_key   = ''
  verbose     = False
  test_mode   = False
  for o,a in opts:
    if o == '-i':
      is_string = True
    elif o == '-s':
      screen_code = True
    elif o == '-t':
      type_delay = int(a)
    elif o == '-j':
      joy_delay = int(a)
    elif o == '-k':
      start_key = a
    elif o == '-v':
      verbose = True
    elif o == '-n':
      test_mode = True

  if is_string:
    data = args[0]
    if screen_code:
      print "ERROR: screen code must be in a file!"
      return False
  else:
    result,data,start,is_prg = app.iotools.read_file(args[0])
    if result != STATUS_OK:
      app.iotools.print_result(result)
      return False
    if screen_code:
      if not is_prg:
        print "ERROR: screen code must be a prg!"
        return False
      if start != 0x400:
        print "ERROR: screen code must begin at 0x0400!"
        return False
    else:
      if is_prg:
        print "ERROR: don't use a prg for type commands!"
        return False

  result,duration = app.dtvcmd.joy_type(data,screen_code=screen_code,
                        type_delay=type_delay,joy_delay=joy_delay,
                        start_key=start_key,verbose=verbose,
                        test_mode=test_mode,callback=app.iotools.print_size_dec)
  app.iotools.print_result(result)
  if result == STATUS_OK:
    app.iotools.print_duration(duration)
    return True
  else:
    return False


def init(cmdSet):

  # joy
  joyCmd = Cmd(["joy"],
  help="joystick commands")
  cmdSet.add_command(joyCmd)

  joyCmd.add_sub_command(Cmd(["type"],
  help="type contents of the given file on the\nvirtual DTV keyboard",
  opts=(1,1,"<file>"),
  args=[
    ('i',None,'type given text as string and not as file'),
    ('s',None,'type given .prg as screen code to 0x0400'),
    ('t','<delay>','set the type delay\n(default: 6)'),
    ('j','<delay>','set the joystick move delay\n(default: 6)'),
    ('k','<key>','assume virtual keyboard has current key\n(default: J)'),
    ('v',None,'verbose the generated joy stream'),
    ('n',None,'test mode: do not execute command')
  ],
  func=joy_type))

  joyCmd.add_sub_command(Cmd(["stream"],
  help="process the joy stream commands given\nin a file or as a string",
  opts=(1,1,"<file>"),
  args=[
    ('i',None,'execute given text directly'),
    ('j','<delay>','set the joystick move delay\n(default: 15)'),
    ('v',None,'verbose the generated commands'),
    ('n',None,'test mode: do not execute command')
  ],
  func=joy_stream))

  joyCmd.add_sub_command(Cmd(["rawkey"],
  help="press a key on virt. keyboard\nby specifying its relative position",
  opts=(2,3,"<x> <y> [<delay>]"),
  func=joy_rawkey))

  joyCmd.add_sub_command(Cmd(["wiggle"],
  help="wiggle joystick left to right",
  opts=(1,2,"<time> [<delay>]"),
  func=joy_wiggle))


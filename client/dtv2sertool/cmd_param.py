#
# cmd_param.py - set/get params of dtv2ser device
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
from dtv2ser.param   import Param
from dtv2sertool.cmd import Cmd
from dtv2sertool.app import app

def param_dump(cmd,args,opts):
  param = Param(app.sercon)
  (result,byte_param,word_param) = param.dump()
  app.iotools.print_result(result)
  if result == STATUS_OK:
    print "byte parameters:"
    pos = 0
    for a in byte_param:
      print "#%02x:   %02x   (%3d) %s" % (pos,a,a,param_byte_name[pos])
      pos += 1
    print "word parameters:"
    pos = 0
    for a in word_param:
      print "#%02x: %04x (%5d) %s" % (pos,a,a,param_word_name[pos])
      pos += 1
    return True
  else:
    return False

def param_reset(cmd,args,opts):
  print "  resetting parameters"
  param  = Param(app.sercon)
  result = param.reset_default()
  app.iotools.print_result(result)
  return result == STATUS_OK

def param_load(cmd,args,opts):
  print "  loading parameters from EEPROM"
  param  = Param(app.sercon)
  result = param.load()
  app.iotools.print_result(result)
  return result == STATUS_OK

def param_save(cmd,args,opts):
  print "  saving parameters to EEPROM"
  param  = Param(app.sercon)
  result = param.save()
  app.iotools.print_result(result)
  return result == STATUS_OK

def param_set_byte(cmd,args,opts):
  num,num_valid = app.iotools.parse_number(args[0])
  val,val_valid = app.iotools.parse_number(args[1])
  if not num_valid or not val_valid:
    print "ERROR: invalid set_byte parameter"
    return False
  print "  setting parameter byte %02d to 0x%04x" % (num,val)
  param  = Param(app.sercon)
  result = param.set_byte(num,val)
  app.iotools.print_result(result)
  return result == STATUS_OK

def param_set_word(cmd,args,opts):
  num,num_valid = app.iotools.parse_number(args[0])
  val,val_valid = app.iotools.parse_number(args[1])
  if not num_valid or not val_valid:
    print "ERROR: invalid set_byte parameter"
    return False
  print "  setting parameter word %02d to 0x%04x" % (num,val)
  param  = Param(app.sercon)
  result = param.set_word(num,val)
  app.iotools.print_result(result)
  return result == STATUS_OK

def init(cmdSet):

  # param
  paramCmd = Cmd(["param"],
  help="parameter commands")
  cmdSet.add_command(paramCmd)

  paramCmd.add_sub_command(Cmd(["dump"],
  help="print all parameters of dtv2ser",
  func=param_dump))

  paramCmd.add_sub_command(Cmd(["reset"],
  help="reset all parameters to default values",
  func=param_reset))

  paramCmd.add_sub_command(Cmd(["load"],
  help="load parameter set from EEPROM",
  func=param_load))

  paramCmd.add_sub_command(Cmd(["save"],
  help="save parameter set to EEPROM",
  func=param_save))

  paramCmd.add_sub_command(Cmd(["set_byte"],
  help="set byte parameter to value",
  opts=(2,2,"<num> <byte>"),
  func=param_set_byte))

  paramCmd.add_sub_command(Cmd(["set_word"],
  help="set word parameter to value",
  opts=(2,2,"<num> <word>"),
  func=param_set_word))


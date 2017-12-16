#
# cmd_boot.py - command for automatic bootstrapping
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
from dtv2sertool.bootstrap import Bootstrap

def bootstrap(cmd,args,opts):

  fast = True
  screen_code = False
  check_files = True
  for o,a in opts:
    if o == '-f':
      fast = False
    elif o == '-s':
      screen_code = True
    elif o == '-c':
      check_files = False
  mode = args[0]

  bs = Bootstrap(app.dtvcmd,fast,screen_code,check_files)
  if mode == "basic":
    result = bs.bootstrap_basic()
  elif mode == "boot":
    result = bs.bootstrap_boot()
  elif mode == "dtvtrans":
    result = bs.bootstrap_dtvtrans()
  elif mode == "full":
    result = bs.bootstrap_full()
  else:
    print "ERROR: unknown bootstrap mode!"
    return False
  app.iotools.print_result(result)
  return result == STATUS_OK


def init(cmdSet):

  # bootstrap
  cmdSet.add_command(Cmd(["bootstrap"],
    help='''bootstrap a DTV with dtv2ser connected
to joystick port 2.

basic     1. reset and boot into basic prompt
boot      2. type in boot.txt basic boot code and run
dtvtrans  3. boot mlboot.prg and dtvtrans.prg
full      1.-3. basic + boot + dtvtrans''',
    opts=(1,1,"<mode>"),
    args=[
      ('f',None,'disable fast mode'),
      ('s',None,'use screen code to type in mlboot.prg\ninstead of boot.txt in the boot stage'),
      ('c',None,'disable file checks on required files')
    ],
    func=bootstrap))

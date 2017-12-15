#
# cmd_server.py - server commands
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

def server_ping(cmd,args,opts):
  print "  pinging dtvtrans: ",
  result = app.dtvcmd.is_alive()
  if result == STATUS_OK:
    print "pong!"
  elif result == TRANSFER_ERROR_NOT_ALIVE:
    print "NOT ALIVE!"
  else:
    app.iotools.print_result(result)
  return result == STATUS_OK or result == TRANSFER_ERROR_NOT_ALIVE


def server_info(cmd,args,opts):
  if not app.require_server_alive():
    return False

  (result,revision) = app.dtvcmd.query_revision_string()
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False
  print "  dtvtrans revision: %s" % revision

  # other info only available in dtvtrans >= 1.0
  if not app.has_dtvtrans_10():
    return True

  (result,impl) = app.dtvcmd.query_implementation()
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False
  print "    implementation:  %s"% impl
  (result,port,mode,start,end) = app.dtvcmd.query_config()
  app.iotools.print_result(result)
  if result != STATUS_OK:
    return False
  print "    port:            %4s" % ("joy1","joy2","usr")[port]
  print "    mode:            %3s" % ("RAM","ROM")[mode]
  print "    range:           0x%06x-0x%06x" % (start,end)
  return True


def server_ram(cmd,args,opts):
  if app.has_dtvtrans_10_in_ram():
    print "  dtvtrans 1.0 is already in RAM!"
    return True
  return app.helper.load_and_run_dtvtrans_ram()


def init(cmdSet):
  # server
  serverCmd = Cmd(["server","srv"],
  help="dtvtrans server commands")
  cmdSet.add_command(serverCmd)

  serverCmd.add_sub_command(Cmd(["ram"],
    help="""setup dtvtrans RAM version""",
    func=server_ram))

  # ping command
  serverCmd.add_sub_command(Cmd(["ping"],
  help='''ping dtvtrans server\nby sending a is-alive command''',
  func=server_ping))

  # info command
  serverCmd.add_sub_command(Cmd(["info"],
  help='''query information about the dtvtrans server''',
  func=server_info))


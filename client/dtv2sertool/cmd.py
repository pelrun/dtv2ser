#
# cmd.py - describe command
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

import getopt
import operator

class CmdError(Exception):
  """CmdSet exception"""
  pass

class Cmd:

  def __init__(self,names,help="",func=None,args=[],opts=(0,0,'')):
    self.names = names
    self.help = help
    self.func  = func
    self.args = args[:]
    self.opts = opts
    self.args.append(('h',None,'help on this command'))
    self.sub_cmds = []
    # create argument pattern
    self.args_pattern = ""
    for g in self.args:
      self.args_pattern += g[0]
      if g[1] != None:
        self.args_pattern += ":"

  def add_sub_command(self,subcmd):
    self.sub_cmds.append(subcmd)

  def show_help(self,indent=2,width=30,short=False):
    help = self.help.split("\n")
    size = width - indent
    format = ' ' * indent + "%-" + str(size) + "s %s"
    names = ' | '.join(self.names) + ' ' + self.opts[2]

    # add on for names
    addon = ""
    if len(self.sub_cmds)>0:
      addon = "<sub command> ..."
    names += addon

    # print main name
    if len(names)>size:
      print format % (names,"")
      print format % ("",help[0])
    else:
      print format % (names,help[0]);
    for h in help[1:]:
      print format % ("",h)
    print

    # short help only show main
    if short:
      return

    # with sub commands
    if len(self.sub_cmds)>0:
      # print sub command
      for c in sorted(self.sub_cmds,key=lambda x:x.names[0]):
        c.show_help(indent=indent+2,width=width)

    # normal command
    else:
      # print arguments
      indent += 4
      size -= 4
      format = ' ' * indent + "%-" + str(size) + "s %s"
      for a in sorted(self.args,key=lambda x:x[0].lower()):
        if a[0] == 'h':
          continue
        switch = '-' + a[0]
        if a[1] != None:
          switch += ' ' + a[1]
        help = a[2].split("\n")
        print format % (switch,help[0])
        for h in help[1:]:
          print format % ("",h)
      if len(self.args)>1:
        print

  def handle_command(self,args,top_commands=[]):
    """Check if the args map to this command
    Return True=handled/False=not handled
    """
    # try to find name
    command = args[0]
    if command not in self.names:
      return False

    tc = top_commands[:]
    tc.append(command)
    tc_str = ' '.join(tc)

    # parse arguments of command
    try:
      opts, args = getopt.getopt(args[1:],self.args_pattern)
    except getopt.GetoptError,e:
      raise CmdError,"Invalid arguments for command '%s' given (%s)" % (tc_str,repr(e))

    # handle help option
    if ('-h','') in opts:
      indent=2
      for t in top_commands:
        print ' ' * indent + t
        indent += 2
      self.show_help(indent=indent)
      return True

    # sub command
    if len(self.sub_cmds)>0:
      if(len(args)==0):
        raise CmdError,"Sub command expected for '%s'" % tc_str
      # find sub command
      for sc in self.sub_cmds:
        if sc.handle_command(args,tc):
          return True
      raise CmdError,"Unknown sub command for '%s': %s" % (tc_str,args[0])

    # normal command

    # check number of options
    min_args = self.opts[0]
    max_args = self.opts[1]
    arg_len = len(args)
    if arg_len<min_args:
      raise CmdError,"Too few arguments for '%s'. Expected %d, but found %d" % (tc_str,min_args,arg_len)
    if arg_len>max_args:
      raise CmdError,"Too many arguments for '%s'. Expected %d, but found %d" % (tc_str,max_args,arg_len)

    # finally execute command
    if not self.func(command,args,opts):
      raise CmdError,"Command failed"

    return True

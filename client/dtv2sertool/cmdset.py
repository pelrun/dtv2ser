#
# cmdset.py - parse and execute command line with a command set
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
from dtv2sertool.cmd import CmdError

class CmdSet:

  def __init__(self,name,global_args=[],global_func=None):
    self.name = name
    self.global_args = global_args
    self.global_func = global_func
    self.commands  = []

    # auto append help switch
    self.global_args.append(('h',None,'show help message'))

    # create argument pattern
    self.global_args_pattern = ""
    for g in self.global_args:
      self.global_args_pattern += g[0]
      if g[1] != None:
        self.global_args_pattern += ":"

  def add_command(self,cmd):
    self.commands.append(cmd)

  def show_help(self,indent=2,width=30):
    print "Usage:",self.name,"[global options] command <local_options> <local_args> [+ command <options>]"
    print

    size = width - indent
    format = ' ' * indent + "%-" + str(size) + "s %s"

    print "Global Options:"
    for g in sorted(self.global_args,key=lambda x:x[0].lower()):
      entry = '-' + g[0]
      help  = g[2].split('\n')
      if g[1] != None:
        entry += ' ' + g[1]
      print format % (entry,help[0])
      for h in help[1:]:
        print format % ("",h)
      print

    print
    print "Commands:"
    for c in sorted(self.commands,key=lambda x:x.names[0].lower()):
      c.show_help(indent=indent,width=width,short=True)
    print "  Use '%s <command> -h' to show more help on a command!" % self.name
    print

  def handle_global_options(self,args):
    """parse the global options"""

    # parse global options first
    try:
      opts, args = getopt.getopt(args,self.global_args_pattern)
    except getopt.GetoptError,e:
      raise CmdError,"Invalid global arguments given (%s)" % repr(e)

    # handle global options
    for o in opts:
      if o[0] == '-h':
        self.show_help()
        return None
      else:
        if self.global_func != None:
          self.global_func(o[0],o[1])

    return args

  def handle_command_line(self,args):
    """parse and execute the rest of the command line"""

    # now split command line into segments separated by '+'
    args_size = len(args)
    args_pos  = 0
    num_cmds = 0
    while args_pos < args_size:

      # find '+' command separator
      cmd_end = args_pos
      while cmd_end < args_size:
        if args[cmd_end] == '+':
          break;
        cmd_end += 1
      if cmd_end == args_pos:
        raise CmdError,"No command given!"

      # extract command
      this_args = args[args_pos:cmd_end]
      args_pos  = cmd_end + 1

      self.execute_segment(this_args)
      num_cmds += 1
    return num_cmds

  def execute_segment(self,args):
    # try to handle command
    handled = False
    for c in self.commands:
       handled = c.handle_command(args)
       if handled:
         break
    if not handled:
      raise CmdError,"Unknown command " + args[0]


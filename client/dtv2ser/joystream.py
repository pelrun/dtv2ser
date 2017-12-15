#
# joystream.py - create joy stream sequences
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

class JoyStream:
  """Create byte streams used for the joy stream command of dtv2ser"""

  def delta_move_to_stream(self,delta,delay):
    """Convert a delta move (dx,dy) of auto type to stream commands
       Returns joystream"""

    # get delta x and y
    x = delta[0]
    y = delta[1]

    # prepare some commands
    d  = chr(delay | JOY_COMMAND_WAIT)
    d2 = chr(delay*2 | JOY_COMMAND_WAIT)
    dw = d + chr(JOY_FIRE) + d

    # press fire
    stream = chr(JOY_FIRE) + d2

    # move delta y
    if y<0:
      for step in xrange(abs(y)):
        stream += chr(JOY_FIRE|JOY_UP) + dw
    elif y>0:
      for step in xrange(y):
        stream += chr(JOY_FIRE|JOY_DOWN) + dw

    # move delta x
    if x<0:
      for step in xrange(abs(x)):
        stream += chr(JOY_FIRE|JOY_LEFT) + dw
    elif x>0:
      for step in xrange(x):
        stream += chr(JOY_FIRE|JOY_RIGHT) + dw

    # releas fire
    stream += chr(JOY_NONE) + d2

    return stream

  # ---------- Single JoyStream ----------

  def generate_delta_move_stream(self,delta,delay):
    """Create a stream for a single move"""
    stream = self.delta_move_to_stream(delta,delay)
    stream += chr(JOY_COMMAND_EXIT)
    return stream

  def generate_wiggle_stream(self,duration,delay):
    """Create a stream of a number of wiggles"""

    duration *= 100
    num_wiggles = duration / delay

    stream = ""
    for i in xrange(num_wiggles):
      m = i % 4
      if m == 0:
        stream += chr(JOY_LEFT)
      elif m == 2:
        stream += chr(JOY_RIGHT)
      else:
        stream += chr(JOY_NONE)
      stream += chr(JOY_COMMAND_WAIT | delay)
    stream += chr(JOY_COMMAND_EXIT)
    return stream

  # ---------- JoyStream Sequences ----------

  dump_map = {
    JOY_NONE : ' ',
    JOY_UP   : '^',
    JOY_DOWN : 'v',
    JOY_LEFT : '<',
    JOY_RIGHT: '>',
  }

  def dump_stream(self,stream):
    """Dump a joy stream"""
    result = "{"
    has_fire = False
    for s in stream:
      c = ord(s)
      cmd = c & JOY_COMMAND_MASK
      val = c & ~JOY_COMMAND_MASK
      if cmd == JOY_COMMAND_EXIT:
        result += "e"
      elif cmd == JOY_COMMAND_WAIT:
        result += "%d" % val
      elif cmd == JOY_COMMAND_OUT:
        current_fire = val & JOY_FIRE == JOY_FIRE
        val &= ~JOY_FIRE
        toggle_fire = False
        if current_fire != has_fire:
          if has_fire:
            result += "]"
          else:
            result += "["
          has_fire = current_fire
          toggle_fire = True
        if self.dump_map.has_key(val):
          code = self.dump_map[val]
          if code != ' ' or not toggle_fire:
            result += code
        else:
          result += "(%x)" % val
      else:
        result += "?"
    result += "}"
    return result

  def dump_stream_seq(self,seq):
    """Dump the joy stream seq"""
    result = ""
    for s in seq:
      what = s[0]
      contents = s[1]
      if what == JoyStream_Commands:
        result += self.dump_stream(contents)
      elif what == JoyStream_Sleep:
        result += "[sleep=%s]" % contents
      else:
        result += "[???]"
    return result

  def estimate_stream_duration(self,stream):
    """Estimate the time for a stream
       Returns seconds"""
    duration = 0.0
    for s in stream:
      c = ord(s)
      cmd = c & JOY_COMMAND_MASK
      val = c & ~JOY_COMMAND_MASK
      if cmd == JOY_COMMAND_WAIT:
        duration += float(val) / 100
    return duration

  def estimate_stream_seq_duration(self,seq):
    """Estimate the time for a stream seq
       Returns seconds"""
    duration = 0.0
    for s in seq:
      what = s[0]
      contents = s[1]
      if what == JoyStream_Commands:
        duration += self.estimate_stream_duration(contents)
      elif what == JoyStream_Sleep:
        duration += float(contents)
    return duration

  def parse_string_stream_seq(self,string,delay):
    """Parse and create a stream from a string notation
       Returns stream_seq,total_commands"""
    js_seq = []
    total = 0

    # convert string to stream
    stream = ""
    max_len = len(string)
    pos = 0
    add_fire = JOY_NONE
    while pos < max_len:

      # delay command
      d = chr(JOY_COMMAND_WAIT | delay)
      dn= d + chr(add_fire) + d

      # get next command
      c = string[pos]
      pos += 1

      # parse a repeat
      repeat = 1
      if c >= '0' and c <= '9':
        repeat = 0
        while c >= '0' and c <= '9' and pos < max_len:
          repeat *= 10
          repeat += ord(c)-ord('0')
          c = string[pos]
          pos += 1

      # joystick control
      if c == 'f':
        stream += (chr(JOY_FIRE  | add_fire) + dn) * repeat
      elif c == 'u':
        stream += (chr(JOY_UP    | add_fire) + dn) * repeat
      elif c == 'd':
        stream += (chr(JOY_DOWN  | add_fire) + dn) * repeat
      elif c == 'l':
        stream += (chr(JOY_LEFT  | add_fire) + dn) * repeat
      elif c == 'r':
        stream += (chr(JOY_RIGHT | add_fire) + dn) * repeat

      # wait a pulse delay
      elif c == '.':
        stream += d

      # split stream and add a wait
      elif c == '*' or c == '+':
        delay = repeat
        if c == '+': # in ms
          delay /= 1000
        # end current stream
        if stream != "":
          stream += chr(JOY_COMMAND_EXIT)
          js_seq.append((JoyStream_Commands,stream))
          total += len(stream)
          stream = ""
        js_seq.append((JoyStream_Sleep,delay))

      # define new delay:
      elif c == ':':
        delay = repeat & 0x1f

      # press and hold fire
      elif c == '[':
        stream += chr(JOY_FIRE) + d
        add_fire = JOY_FIRE
      # releas fire
      elif c == ']':
        stream += chr(JOY_NONE) + d
        add_fire = JOY_NONE

      else:
        print "UNKNOWN character in JoyStream:",c

    # end current stream
    if stream != "":
      stream += chr(JOY_COMMAND_EXIT)
      js_seq.append((JoyStream_Commands,stream))
      total += len(stream)

    return js_seq,total

  def convert_autotype_seq(self,at_stream):
    """Convert a sequence of auto type commands to a joy stream sequence
       Returns joystream_seq,total_bytes."""
    stream_seq = []
    total = 0

    for at_cmd in at_stream:
      cmd = at_cmd[0]
      delay = at_cmd[1]

      # convert delta move to joy stream
      if cmd == AutoType_DeltaMove:
        stream = self.delta_move_to_stream(at_cmd[2:],delay)
        stream += chr(JOY_COMMAND_EXIT)
        total += len(stream)
        stream_seq.append((JoyStream_Commands,stream))
      # parse an embedded joy stream
      elif cmd == AutoType_JoyStream:
        seq,num = self.parse_string_stream_seq(at_cmd[2],delay)
        stream_seq += seq
        total += num
      # unknown command
      else:
        print "UNNOWN AutoType Command",cmd

    # return optimized stream
    return self.optimize_joystream_seq(stream_seq),total

  def optimize_joystream_seq(self,js_seq):
    """Optimize joy stream sequence by packing joystream commands
       Returns opt_js_seq"""
    last_stream = ""
    new_seq = []
    for entry in js_seq:
      cmd = entry[0]
      # is a command
      if cmd == JoyStream_Commands:
        stream = entry[1]
        last_stream += stream[0:-1]
      # no command stream
      else:
        # was last stream
        if last_stream != "":
          last_stream += chr(JOY_COMMAND_EXIT)
          new_seq.append((JoyStream_Commands,last_stream))
          last_stream = ""
        new_seq.append(entry)

    # finish last command
    if last_stream != "":
      last_stream += chr(JOY_COMMAND_EXIT)
      new_seq.append((JoyStream_Commands,last_stream))
    return new_seq

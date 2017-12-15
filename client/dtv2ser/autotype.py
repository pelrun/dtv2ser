#
# autotype.py - handle typing on the virtual joystick keyboard of the DTV
#
# Heavily based on the original autotype developed by:
#  Mikkel Holm Olsen AKA Spiff
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

class AutoType:
  """The AutoType class handles the movement patterns required to
     enter a sequence of characters with the DTV virtual keyboard"""

  # the autotype_map maps a valid character to a keyboard matrix position
  # and a shift state.
  autotype_map = {
    # special characters
   '\n':(14, 2,False), # LF
   '\r':(14, 2,False), # CR
   'n': (14, 2,False), # CR
   'd': (14, 3,False), # cursor down
   'u': (14, 3,True),  # cursor up
   'l': (15, 3,True),  # cursor left
   'r': (15, 3,False), # cursor right
   'h': (14, 0,False), # home
   'i': (13, 1,False), # arrow up
   'j': ( 0, 0,False), # arrow left
   'c': ( 0, 1,False), # ctrl
   'o': ( 0, 3,False), # c=
   'p': (13, 0,False), # Pound sign
    # supported characters
   ' ': ( 8, 4,False),
   '!': ( 1, 0,True),
   '"': ( 2, 0,True),
   '#': ( 3, 0,True),
   '$': ( 4, 0,True),
   '%': ( 5, 0,True),
   '&': ( 6, 0,True),
   '\'':( 7, 0,True),
   '(': ( 8, 0,True),
   ')': ( 9, 0,True),
   '*': (12, 1,False),
   '+': (11, 0,False),
   ',': ( 9, 3,False),
   '-': (12, 0,False),
   '.': (10, 3,False),
   '/': (11, 3,False),
   '0': (10, 0,False),
   '1': ( 1, 0,False),
   '2': ( 2, 0,False),
   '3': ( 3, 0,False),
   '4': ( 4, 0,False),
   '5': ( 5, 0,False),
   '6': ( 6, 0,False),
   '7': ( 7, 0,False),
   '8': ( 8, 0,False),
   '9': ( 9, 0,False),
   ':': (11, 2,False),
   ';': (12, 2,False),
   '<': ( 9, 3,True),
   '=': (13, 2,False),
   '>': (10, 3,True),
   '?': (11, 3,True),
   '@': (11, 1,False),
   'A': ( 2, 2,False),
   'B': ( 6, 3,False),
   'C': ( 4, 3,False),
   'D': ( 4, 2,False),
   'E': ( 3, 1,False),
   'F': ( 5, 2,False),
   'G': ( 6, 2,False),
   'H': ( 7, 2,False),
   'I': ( 8, 1,False),
   'J': ( 8, 2,False),
   'K': ( 9, 2,False),
   'L': (10, 2,False),
   'M': ( 8, 3,False),
   'N': ( 7, 3,False),
   'O': ( 9, 1,False),
   'P': (10, 1,False),
   'Q': ( 1, 1,False),
   'R': ( 4, 1,False),
   'S': ( 3, 2,False),
   'T': ( 5, 1,False),
   'U': ( 7, 1,False),
   'V': ( 5, 3,False),
   'W': ( 2, 1,False),
   'X': ( 3, 3,False),
   'Y': ( 6, 1,False),
   'Z': ( 2, 3,False),
   '[': (11, 2,True),
   '\\':(13, 0,False),  # Pound sign
   ']': (12, 2,True)
  }

  def __init__(self):
    # setup initial delays
    self.type_delay = 6
    self.joy_delay  = 6
    self.reset_state()

  def reset_state(self):
    """Reset Autotype state"""
    # initial position in virtual keyboard: J (8,2)
    self.last_x = 8
    self.last_y = 2
    self.shift_state = False

  def save_state(self):
    """Save the current Autotype state"""
    self.save_last_x = self.last_x
    self.save_last_y = self.last_y
    self.save_shift_state = self.shift_state

  def restore_state(self):
    """Restore the last saved Autotype state"""
    self.last_x = self.save_last_x
    self.last_y = self.save_last_y
    self.shift_state = self.save_shift_state

  def setup(self,start_key,type_delay,joy_delay):
    """Setup AutoType with a given state"""
    if type_delay != 0:
      self.type_delay = type_delay
    if joy_delay != 0:
      self.joy_delay  = joy_delay

    if start_key != "":
      if self.autotype_map.has_key(start_key):
        # fetch key's position in keymap layout and shift state
        key_info = self.autotype_map[start_key]
        self.last_x = key_info[0]
        self.last_y = key_info[1]
        self.shift_state = key_info[2]
      else:
        return CLIENT_ERROR_INVALID_ARGUMENT
    return STATUS_OK

  def parse_special_seq(self,at_seq,seq):
    """Parse embedded sequence in {...} block
       This is either a joy stream of a auto type internal command {:...}"""
    if seq == "":
      return

    # autotype internal command
    if seq[0] == ':':
      cmds = seq[1:].split(',')
      for c in cmds:
        # single char commands
        if c == 'R':
          self.reset_state()
          at_seq.append((AutoType_JoyStream,self.joy_delay,"*")) # wait a second
        # assing commands
        else:
          assignment = c.split('=')
          if len(assignment) != 2:
            print "INVALID AutoType special sequence:",c
          else:
            var = assignment[0]
            value = assignment[1]
            if var == 't':
              self.type_delay = int(value)
            elif var == 'j':
              self.joy_delay = int(value)
            else:
              print "UNKNOWN AutoType special sequence:",var

    # joy stream
    else:
      at_seq.append((AutoType_JoyStream,self.joy_delay,seq))

  def add_move(self,at_seq,x,y):
    """Add a move to x,y to the sequence list"""

    # calc expected delta movement from last position on grid keymap
    dx = ((x - self.last_x + 17 + 8) % 17) - 8
    dy = ((y - self.last_y + 5 + 2) % 5) - 2

    # calc real delta y movement on real keymap
    real_dy = 0
    if dy > 0:
      sign = 1
    else:
      sign = -1
    while y != self.last_y:
      real_dy += sign
      if self.last_x == 15:
        if self.last_y == 0 and sign == 1: # RESTORE
          self.last_x = 14
        if self.last_y == 3 and sign == -1: # CRSR
          self.last_x = 14
      if self.last_x == 13:
        if self.last_y == 2 and sign == 1: # SHIFT right
          self.last_x = 12
        if self.last_y == 4 and sign == -1: # SHIFT right
          self.last_x = 12
      self.last_y = (self.last_y + sign + 5) % 5

    # calc real delta x movement on real keymap
    real_dx = 0
    if dx > 0:
      sign = 1
    else:
      sign = -1
    while x != self.last_x:
      real_dx += sign
      if self.last_y == 3:
        if self.last_x == 12 and sign == 1: # SHIFT right
          self.last_x = 13
        if self.last_x == 14 and sign == -1: # SHIFT right
          self.last_x = 13
      if self.last_y == 1 or self.last_y == 2:
        if self.last_x == 14 and sign == 1: # RESTORE/RETURN
          self.last_x = 15
        if self.last_x == 16 and sign == -1: # RESTORE/RETURN
          self.last_x = 15
      self.last_x = (self.last_x + sign + 17) % 17

    # add to delta list
    at_seq.append((AutoType_DeltaMove,self.type_delay,real_dx,real_dy))

  def convert_string_to_autotype_seq(self,text):
    """Convert a string to list of delta (x,y) movements required
       to be performed on the virtual keyboard to enter the string.
       Every character gets a delta pair. Additionally, SHIFT delta
       pairs are inserted if required."""

    # add initial stream with type delay
    at_seq = []

    force_shift = False
    ignore_shift = False

    # for all characters in text
    text_len = len(text)
    pos = 0
    while pos < text_len:

      # get next character
      c = text[pos]
      shift_toggle = False

      # SPACE is valid on every x posiiton
      if c == ' ' or c == 's':
        x=self.last_x
        y=4

      # SHIFT can be toggled with '_'
      elif c == '_':
        if self.last_x > 7:
          x = 12
        else:
          x = 1
        y=3
        self.shift_state = not self.shift_state
        ignore_shift = self.shift_state

      # '~' toggle c= state
      elif c == '~':
        x = 0
        y = 3

      # '^' set shift for next char
      elif c == '^':
        if not self.shift_state:
          if self.last_x > 7:
            x = 12
          else:
            x = 1
          y=3
          self.shift_state = True
        force_shift = True

      # key is in map and available
      elif self.autotype_map.has_key(c):
        # fetch key's position in keymap layout and shift state
        key_info = self.autotype_map[c]
        x = key_info[0]
        y = key_info[1]

        if ignore_shift:
          pass
        elif force_shift:
          force_shift = False
        else:
          shifted = key_info[2]

          # key needs a different shift state
          if shifted != self.shift_state:
            shift_toggle = True
            if self.last_x > 7:
              x = 12
            else:
              x = 1
            y = 3

      # special sequence block
      elif c == '{':
        end = text.find('}',pos)
        if end != -1:
          seq = text[pos+1:end]
          pos = end + 1
          self.parse_special_seq(at_seq,seq)
        else:
          pos += 1
        continue

      # not a valid key found
      else:
        print "INVALID key",c
        pos += 1
        continue

      self.add_move(at_seq,x,y)

      # restore shift state
      if shift_toggle:
        shift_toggle = False
        self.shift_state = not self.shift_state
      else:
        pos += 1

    return at_seq

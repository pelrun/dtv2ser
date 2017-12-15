#
# screencode.py - directly type in assembly programs as screen code
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

class ScreenCode:
  """Directly type in Screen Code"""

  # map a byte value to the associated key and shift+cbm state
  # map only 0x00-0x7f as 0x80-0xff use the same keys but reverse mode on
  bin_map = [
    # 0
    ['@', False, False] ,
    ['A', False, False] ,
    ['B', False, False] ,
    ['C', False, False] ,
    ['D', False, False] ,
    ['E', False, False] ,
    ['F', False, False] ,
    ['G', False, False] ,
    ['H', False, False] ,
    ['I', False, False] ,
    # 10
    ['J', False, False] ,
    ['K', False, False] ,
    ['L', False, False] ,
    ['M', False, False] ,
    ['N', False, False] ,
    ['O', False, False] ,
    ['P', False, False] ,
    ['Q', False, False] ,
    ['R', False, False] ,
    ['S', False, False] ,
    # 20
    ['T', False, False] ,
    ['U', False, False] ,
    ['V', False, False] ,
    ['W', False, False] ,
    ['X', False, False] ,
    ['Y', False, False] ,
    ['Z', False, False] ,
    [':', True, False] ,
    ['p', False, False] ,
    [';', True, False] ,
    # 30
    ['i', False, False] ,
    ['j', False, False] ,
    [' ', False, False] ,
    ['1', True, False] ,
    ['2', True, False] ,
    ['3', True, False] ,
    ['4', True, False] ,
    ['5', True, False] ,
    ['6', True, False] ,
    ['7', True, False] ,
    # 40
    ['8', True, False] ,
    ['9', True, False] ,
    ['*', False, False] ,
    ['+', False, False] ,
    [',', False, False] ,
    ['-', False, False] ,
    ['.', False, False] ,
    ['/', False, False] ,
    ['0', False, False] ,
    ['1', False, False] ,
    # 50
    ['2', False, False] ,
    ['3', False, False] ,
    ['4', False, False] ,
    ['5', False, False] ,
    ['6', False, False] ,
    ['7', False, False] ,
    ['8', False, False] ,
    ['9', False, False] ,
    [':', False, False] ,
    [';', False, False] ,
    # 60
    [',', True, False] ,
    ['=', False, False] ,
    ['.', True, False] ,
    ['/', True, False] ,
    ['*', True, False] ,
    ['A', True, False] ,
    ['B', True, False] ,
    ['C', True, False] ,
    ['D', True, False] ,
    ['E', True, False] ,
    # 70
    ['F', True, False] ,
    ['G', True, False] ,
    ['H', True, False] ,
    ['I', True, False] ,
    ['J', True, False] ,
    ['K', True, False] ,
    ['L', True, False] ,
    ['M', True, False] ,
    ['N', True, False] ,
    ['O', True, False] ,
    # 80
    ['P', True, False] ,
    ['Q', True, False] ,
    ['R', True, False] ,
    ['S', True, False] ,
    ['T', True, False] ,
    ['U', True, False] ,
    ['V', True, False] ,
    ['W', True, False] ,
    ['X', True, False] ,
    ['Y', True, False] ,
    # 90
    ['Z', True, False] ,
    ['+', True, False] ,
    ['-', False, True] ,
    ['-', True, False] ,
    ['i', True, False] ,
    ['*', False, True] ,
    [' ', True, False] ,
    ['K', False, True] ,
    ['I', False, True] ,
    ['T', False, True] ,
    # 100
    ['@', False, True] ,
    ['G', False, True] ,
    ['+', False, True] ,
    ['M', False, True] ,
    ['p', False, True] ,
    ['p', True, False] ,
    ['N', False, True] ,
    ['Q', False, True] ,
    ['D', False, True] ,
    ['Z', False, True] ,
    # 110
    ['S', False, True] ,
    ['P', False, True] ,
    ['A', False, True] ,
    ['E', False, True] ,
    ['R', False, True] ,
    ['W', False, True] ,
    ['H', False, True] ,
    ['J', False, True] ,
    ['L', False, True] ,
    ['Y', False, True] ,
    # 120
    ['U', False, True] ,
    ['O', False, True] ,
    ['@', True, False] ,
    ['F', False, True] ,
    ['C', False, True] ,
    ['X', False, True] ,
    ['V', False, True] ,
    ['B', False, True]
  ]

  state_shift = 1
  state_cbm   = 2
  state_rev   = 4

  def __init__(self,verbose,autoType,joyStream):
    self.verbose   = verbose
    self.autoType  = autoType
    self.joyStream = joyStream

  def convert_binary_to_type_string(self,bin):
    """Convert a binary sequence to typeable key/screen codes
       Return ats"""

    seq = "h" # start with a home

    last_state = 0
    total_duration = 0

    # process the binary in screen lines a 40 chars
    total = len(bin)
    pos = 0
    line_count = 0
    while pos < total:
      line_len  = min(40,total-pos)
      line_data = bin[pos:pos+line_len]
      pos += line_len

      # find best sweeps for line
      code,last_state,duration = self.find_best_sweeps_for_line(line_data,last_state)
      if self.verbose:
        print "LINE %2d: %.2fsecs" % (line_count,duration)

      seq += code
      line_count += 1
      total_duration += duration

    # add a SYS1024 and make sure that the state is sane
    seq += self.generate_key_state_change(last_state,last_state & self.state_rev)
    seq += "SYS1024n"

    if self.verbose:
      print "TOTAL  : %.2fsecs" % total_duration

    return seq

  def build_best_sweep_lists(self,last_state,sweep):
    """Build a list of sweeps with minimal state changes
       Returns list_of_sweep_lists"""
    init_list = list(sweep)
    size = len(init_list)
    if size == 1:
      return [init_list]

    bit_count = (
      0, # 0
      1, # 1
      1, # 2
      2, # 3
      1, # 4
      2, # 5
      2, # 6
      3, # 7
    )

    # find all entries with minimal state change to last_state
    min_change_bits = 4
    min_bits = []
    for a in init_list:
      state_value = a[1]
      change_bits = last_state ^ state_value
      num_change_bits = bit_count[change_bits]
      if num_change_bits < min_change_bits:
        min_change_bits = num_change_bits
      min_bits.append(num_change_bits)

    # now generate sweep lists for all min entries
    min_entries = []
    pos = 0
    for a in init_list:
      if min_bits[pos] == min_change_bits:
        # remove a from list
        new_sweep = init_list[:pos] + init_list[pos+1:]
        new_lists = self.build_best_sweep_lists(state_value,new_sweep)
        # append all results
        for b in new_lists:
          min_entries.append([a] + b)

      pos += 1

    return min_entries

  def find_best_sweeps_for_line(self,line_data,last_state):
    """Find the set of line sweeps that minimize the type duration
       Return (ats,new_last_state,duration)"""

    # define a sweep by a state mask and a state value
    sweep_map = (
      ((0,0),),
      ((1,0),(1,1)),
      ((2,0),(2,2)),
      ((3,0),(3,1),(3,2),(3,3)),
      ((4,0),(4,4)),
      ((5,0),(5,1),(5,4),(5,5)),
      ((6,0),(6,2),(6,4),(6,6)),
      ((7,0),(7,1),(7,2),(7,3),(7,4),(7,5),(7,6),(7,7))
    )

    all_sweeps = []
    best_sweep = {}

    # try all combinations of possible state skips + sweeps per line
    #  0 = no state skip, only one sweep
    #  1 = shift skip
    #  2 = cbm skip
    #  3 = shift + cbm skip
    #  4 = rev skip
    #  5 = shift + rev skip
    #  6 = cbm + rev skip
    #  7 = shift + cbm + rev skip
    num = 0
    for skip_mask in xrange(8):
      sweeps_seq = sweep_map[skip_mask]
      sweeps_list = self.build_best_sweep_lists(last_state,sweeps_seq)

      for sweep in sweeps_list:
        res,valid = self.do_full_line_sweep(line_data,last_state,sweep)

        if self.verbose:
          duration = res[2]
          print "attempt %d:" % num
          print "  skip_mask: %d" % skip_mask
          print "  sweep:    ",sweep
          print "  duration:  %.2f\r" % duration
          print "  valid:    ",valid

        if valid:
          all_sweeps.append(res)
          duration = res[2]
          best_sweep[duration] = num
          num += 1

    # find best sweep
    keys = best_sweep.keys()
    keys.sort()
    shortest_duration = keys[0]
    shortest_index = best_sweep[shortest_duration]
    if self.verbose:
      print "  -> shortest duration:",shortest_duration,"at attempt",shortest_index

    return all_sweeps[shortest_index]

  def do_full_line_sweep(self,line_data,last_state,sweeps):
    """Perform n-sweeps over a line
       Return (ats,new_last_state,duration),valid"""
    # loop over all sweeps required in the current skip_mask entry
    sweep_code = ""
    sweep_state = last_state
    sweep_damage = []
    num_sweep = 0
    max_sweep = len(sweeps)
    for s in sweeps:
      state_mask  = s[0]
      state_value = s[1]

      # generate code for a sweep
      code,sweep_state = self.line_sweep(line_data,sweep_state,state_mask,state_value,sweep_damage)

      # if a sweep was done then move back to line
      if code != "" and num_sweep < (max_sweep-1):
        code += "{u}"

      sweep_code += code
      num_sweep += 1

    # estimate the duration for all sweeps
    sweep_duration = self.estimate_type_duration(sweep_code)

    # is sweep valid? i.e. has no damage left?
    valid = (len(sweep_damage) == 0)

    return ((sweep_code,sweep_state,sweep_duration),valid)

  def estimate_type_duration(self,ats):
    """Estimate the duration for typing in the given autotype string.
       Returns seconds"""
    self.autoType.save_state()
    at_seq=self.autoType.convert_string_to_autotype_seq(ats)
    js_seq,total_commands=self.joyStream.convert_autotype_seq(at_seq)
    js_dur=self.joyStream.estimate_stream_seq_duration(js_seq)
    self.autoType.restore_state()
    return js_dur

  def line_sweep(self,line_data,last_state,state_mask,state_value,sweep_damage):
    """Generate code for a line sweep. Select only characters whose
       state_mask'ed value has the given state_value.
       Generate state changes where required. Emits cursors jumps for
       skipped characters.

       Returns (auto_type_seq,new_last_state)"""

    ats = ""
    damaged_next = False
    pos = 0
    skip_start = -1
    any_key_emitted = False
    for d in line_data:
      c = ord(d)
      (key,state) = self.byte_to_key_and_state(c)

      # emit key in this sweep?
      do_emit_key = (state & state_mask) == state_value
      if do_emit_key:
        # always remove damage state of last one
        damaged_next = False

        # need to emit a old skip seq first?
        if skip_start != -1:
          skip_len = pos - skip_start
          ats += "{%dr}" % skip_len

        # reset skip flag
        skip_start = -1

        # need a state change?
        if state != last_state:
          ats += self.generate_key_state_change(last_state,state)
          last_state = state

        # special handling for ""
        if key == '2' and (state & self.state_shift == self.state_shift):
          ats += key + key + '{l}'
          damaged_next = True
        else:
          ats += key

        any_key_emitted = True

        # remove key if it is in sweep damage
        if sweep_damage.count(pos) > 0:
          sweep_damage.remove(pos)

      # skip this char
      else:
        # this char was damaged by last emit key
        if damaged_next:
          sweep_damage.append(pos)
          damaged_next = False

        # begin a skip
        if skip_start == -1:
          skip_start = pos

      pos += 1

    # short last line?
    if pos < 40:
      if skip_start == -1:
        skip_start = pos
      pos = 40

    # a final skip required?
    if skip_start != -1:
      skip_len = pos - skip_start
      ats += "{%dr}" % skip_len

    # do not generate code if no key was emitted
    if not any_key_emitted:
      ats = ""

    return ats,last_state

  def generate_key_state_change(self,old_state,new_state):
    """Generate a key sequence to realize a state change.

       Returns (auto_type_seq)"""
    what_changed = old_state ^ new_state
    toggle_shift = what_changed & self.state_shift == self.state_shift
    toggle_cbm   = what_changed & self.state_cbm   == self.state_cbm
    toggle_rev   = what_changed & self.state_rev   == self.state_rev

    enable_shift = new_state & self.state_shift == self.state_shift
    enable_cbm   = new_state & self.state_cbm   == self.state_cbm
    enable_rev   = new_state & self.state_rev   == self.state_rev

    # --- code generation ---
    code = ""

    # toggle reverse
    if toggle_rev:
      # disable old shift state
      if old_state & self.state_shift == self.state_shift:
        code += "_"
      # disable old cbm state
      if old_state & self.state_cbm == self.state_cbm:
        code += "~"

      # establish reverse state
      if enable_rev:
        code += "c9c"
      else:
        code += "c0c"

      # set new cbm state
      if enable_cbm:
        code += "~"
      # set new shift state
      if enable_shift:
        code += "_"

    # no reverse toggling:
    else:
      # toggle shift+cbm
      if toggle_shift and toggle_cbm:
        if enable_shift and not enable_cbm:
          code += "~_"
        else:
          code += "_~"
      elif toggle_shift:
        code += "_"
      elif toggle_cbm:
        code += "~"

    return code

  def byte_to_key_and_state(self,code):
    """Pass in a byte value and return a key and shift + ctrl state.
       Returns (key,state)"""
    reverse = (code > 127)
    lookup  = code & 0x7f
    val = self.bin_map[lookup][:] # copy list
    state = 0
    if val[1]:
      state |= self.state_shift
    if val[2]:
      state |= self.state_cbm
    if reverse:
      state |= self.state_rev
    return (val[0],state)



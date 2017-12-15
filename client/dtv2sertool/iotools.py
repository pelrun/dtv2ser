#
# iotools.py - misc input/output tools
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

import sys, os
from dtv2ser.status import *

class IOTools:
  """Various Tools for input output."""

  def __init__(self):
    self.force_raw_mode = False
    self.force_prg_mode = False
    self.verbose = False

  # ----- Input -----

  def parse_number(self,n):
    """Parse a number given as hex 0x or dec string.
       Returns (number,valid)
    """
    prefix = n[0:2]
    try:
      if prefix == '0x':
        return (int(n[2:],16),True)
      else:
        return (int(n),True)
    except:
      return (0,False)

  def parse_range(self,r):
    """Parse a range and rom flag: [r]<start>-<end> or [r]<start>,<length>
       Returns (rom,start,length,valide)
    """
    if r[0]=='r':
      rom = 1
      r = r[1:]
    else:
      rom = 0
    start  = -1
    length = -1
    pos    = r.find('-')
    if pos != -1:
       start,start_valid = self.parse_number(r[0:pos])
       end,end_valid     = self.parse_number(r[pos+1:])
       if end > start:
         length = end - start
    else:
      pos = r.find(',')
      if pos != -1:
        start,start_valid = self.parse_number(r[0:pos])
        length,end_valid  = self.parse_number(r[pos+1:])
    valid = (start>=0) and (length>=0) and start_valid and end_valid
    return (rom,start,length,valid)

  def parse_write_start(self,arg):
    """Parse range of a write operation
       Returns: (rom,start)  rom=-1 on error
    """
    if arg[0]=='r':
      rom = 1
      arg = arg[1:]
    else:
      rom = 0
    start,valid = self.parse_number(arg)
    if not valid:
      print "ERROR: start addr invalid"
      return(-1,0)
    return (rom,start)

  # ----- Output -----

  def print_result(self,result):
    """Print the result of an operation
       Returns: -
    """
    if result!=STATUS_OK:
      print "    result: %04x %s" % (result,get_result_string(result))

  def print_duration(self,duration):
    """Print the result of an operation
       Returns: -
    """
    print "  duration: %s" % self.time_string(duration)

  def print_transfer_result(self,result,stat):
    """Print results of a transfer operation
       Returns: -
    """
    cr = stat[0]
    sr = stat[1]
    t  = stat[2]
    l  = stat[3]
    self.print_result(result)
    if result == STATUS_OK:
      print "    speed:  client=%02.2f server=%02.2f (kbyte/s)" % (cr,sr)
      print "    time:   %s for %d/0x%06x bytes" % (self.time_string(t),l,l)

  def print_size(self,size):
    """Print size callback for transfer operaitons
       Returns: -
    """
    print " %06x\r" % size,
    sys.stdout.flush()

  def print_size_dec(self,size):
    """Print size callback for transfer operaitons
       Returns: -
    """
    print " %d\r" % size,
    sys.stdout.flush()

  def print_range(self,start,length,verbose=False):
    """Print a range
       Returns: -
    """
    if self.verbose or verbose:
      print "    start:  %06x" % start
      print "    length: %06x" % length
      print "    end:    %06x" % (start + length)

  def time_string(self,seconds):
    """Convert time fraction in seconds to time format"""
    secs  = int(seconds)
    msecs = int((seconds - secs) * 1000)
    mins  = int(secs / 60)
    secs -= mins * 60
    return "%02d:%02d.%03d" % (mins,secs,msecs)

  def status_reg_string(self,sr):
    """Convert SR to string"""
    flags="NV-BDIZC"
    mask=0x80
    result=""
    for x in xrange(8):
      if (sr & mask)==mask:
        result += flags[x]
      else:
        result += "_"
      mask >>= 1
    return result

  # ----- File I/O -----

  def test_file(self,name,main_dir,sub_dir):
    test_path = os.path.join(main_dir,sub_dir)
    file_name = os.path.join(test_path,name)
    if os.path.exists(file_name):
      return file_name
    test_path = main_dir
    file_name = os.path.join(test_path,name)
    if os.path.exists(file_name):
      return file_name
    return ""

  def find_dist_file(self,name,sub_dir="."):
    """Find a distribution file
    Return path or ''
    """
    try_paths = []

    # try current dir + subdir
    file_name = self.test_file(name,os.curdir,sub_dir)
    if file_name != "":
      return file_name
    try_paths.append(os.curdir)

    # try prog dir
    prog = os.path.realpath(sys.argv[0])
    prog_dir = os.path.dirname(prog)
    file_name = self.test_file(name,prog_dir,sub_dir)
    if file_name != "":
      return file_name
    try_paths.append(prog_dir)

    # try prog base dir
    prog_dir = os.path.abspath(os.path.join(prog_dir,".."))
    file_name = self.test_file(name,prog_dir,sub_dir)
    if file_name != "":
      return file_name
    try_paths.append(prog_dir)

    print "ERROR: can't find dist file",name," in ",try_paths
    return ""

  def detect_type(self,name):
    """Detect file type.
       Returns valid,is_prg."""
    if self.force_raw_mode:
      return True,False
    if self.force_prg_mode:
      return True,True
    # check extension
    pos = name.rfind('.')
    if pos == -1:
      print "ERROR: file '%s' has no extension! Please specify mode with -r or -l!" % name
      return False,False
    ext = name[pos+1:].lower()
    if ext == 'prg':
      return True,True
    elif ext in ('raw','bin','txt','img'):
      return True,False
    else:
      print "ERROR: file '%s' has unknown extension! Please specify mode with -r or -l!" % name
      return False,False

  def write_file(self,name,data,start,verbose=True):
    """Write a file to disk
       Returns: status,is_prg
    """
    valid,is_prg = self.detect_type(name)
    if not valid:
      return CLIENT_ERROR_FILE_ERROR,False
    if start > 0xffff and is_prg:
      print "WARNING: file load address will be cropped: 0x%04x" % (start & 0xffff)
    try:
      l=len(data)
      if verbose:
        if is_prg:
          print "  saving prg file '%s': %d/0x%06x bytes, start: 0x%04x" % (name,l,l,start)
        else:
          print "  saving raw file '%s': %d/0x%06x bytes" % (name,l,l)
      f = file(name,'wb')
      # write start address
      if is_prg:
        lo = start & 0xff
        hi = (start >> 8) & 0xff
        f.write(chr(lo)+chr(hi))
      # write data
      f.write(data)
      f.close()
      return STATUS_OK,is_prg
    except:
      return CLIENT_ERROR_FILE_ERROR,False

  def read_file(self,name,verbose=True):
    """Read a file from disk
       Returns: status,data,start,is_prg
    """
    valid,is_prg = self.detect_type(name)
    if not valid:
      return CLIENT_ERROR_FILE_ERROR,"",0,False
    try:
      if verbose:
        if is_prg:
          print "  loading prg file '%s':" % name,
        else:
          print "  loading raw file '%s':" % name,
      start = 0
      f = file(name,'rb')
      if is_prg:
        lohi = f.read(2)
        start = ord(lohi[0]) + ord(lohi[1]) * 256
      data = f.read()
      f.close()
      l = len(data)
      if verbose:
        if is_prg:
          print "%d/0x%06x bytes, start: 0x%04x" % (l,l,start)
        else:
          print "%d/0x%06x bytes" % (l,l)
      return (STATUS_OK,data,start,is_prg)
    except:
      return CLIENT_ERROR_FILE_ERROR,"",0,False

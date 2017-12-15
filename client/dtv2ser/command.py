#
# command.py - dtv2ser high level commands
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

from dtv2ser.status   import *
from dtv2ser.cmdline  import *
from dtv2ser.sercon   import *
from dtv2ser.transfer import *
from dtv2ser.autotype import *
from dtv2ser.joystream import *
from dtv2ser.screencode import *
from dtv2ser.state import State

class Command:
  """The high level commands of dtv2ser."""

  # client version: 0.5
  client_major = 0
  client_minor = 5

  def __init__(self,con):
    self.cmdline   = CmdLine(con)
    self.transfer  = Transfer(con)
    self.autoType  = AutoType()
    self.joyStream = JoyStream()
    self.state     = State(self)

  # ----- version -----------------------------------------------------------

  def get_server_version(self):
    """Return version of dtv2ser firmware.
    Returns (status,major,minor)
    """
    result = self.cmdline.do_command('v')
    if result != STATUS_OK:
      return (result,0,0)
    (result,version) = self.cmdline.get_word()
    major = version >> 8
    minor = version & 0xff
    return (result,major,minor)

  def get_client_version(self):
    """Return version of client"""
    return (self.client_major,self.client_minor)

  def is_compatible_version(self,server_major,server_minor):
    """Check if host and server versions are compatible.
    Return True or False
    """
    return self.client_major == server_major and \
           self.client_minor == server_minor

  # ----- dtv client commands -----------------------------------------------

  def read_memory(self,rom,start,length,callback=lambda x:True,block_size=0x400):
    """Read a memory block from the DTV.
    Return (result,data,client_rx_rate,server_rx_rate).
    """
    cmd = "r%02x%06x%06x" % (rom,start,length)
    self.transfer.begin_rx_rates()
    (result,data) = self.transfer.do_receive_command(cmd,start,length,callback=callback,block_size=block_size);
    stat          = self.transfer.get_rx_rates(length)
    return (result,data,stat)

  def write_memory(self,rom,start,data,callback=lambda x:True,block_size=0x400):
    """Write a memory block to the DTV
    Return (result,client_tx_rate,server_tx_rate).
    """
    cmd = "w%02x%06x%06x" % (rom,start,len(data))
    self.transfer.begin_tx_rates()
    result    = self.transfer.do_send_command(cmd,start,data,callback=callback,block_size=block_size)
    stat      = self.transfer.get_tx_rates(len(data))
    return (result,stat)

  def write_boot_memory(self,start,data,callback=lambda x:True):
    """Write a boot memory block to the DTV
    Return (result,client_tx_rate,server_tx_rate).
    """
    self.transfer.begin_tx_rates()
    result    = self.transfer.do_send_boot(start,data,callback=callback)
    stat      = self.transfer.get_tx_rates(len(data))
    return (result,stat)

  def dtv_reset(self,mode=RESET_NORMAL):
    """Reset the DTV and enter dtvtrans if dtvmon is available.
    Return result.
    """
    result = self.cmdline.do_command("x%02x" % mode)
    if result != STATUS_OK:
      return result
    result = self.cmdline.get_status_byte()
    # a reset invalidates the state
    self.state.invalidate()
    return result

  # ----- dtvtrans commands -------------------------------------------------

  def is_alive(self,timeout=0.5):
    """Perform a is-alive command. This checks wether the dtvtrans server is running and answers.
    Return result.
    """
    tms = timeout * 100
    result = self.cmdline.do_command("a%04x" % tms)
    if result != STATUS_OK:
      return result
    result = self.cmdline.wait_for_server(timeout)
    if result != STATUS_OK:
      return result
    return self.cmdline.get_status_byte()

  def lohi(self,addr):
    """Simple tool for addr conversion"""
    lo = addr & 0xff
    hi = addr >> 8
    return (lo,hi)

  def execute_memory(self,addr):
    """dtvtrans command: CMD_EXECUTE_MEMORY
    Return result.
    """
    cmd = "c0300%02x%02x" % self.lohi(addr)
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result
    return self.cmdline.get_status_byte()

  def sys(self,ptr,sr=0,acc=0,xr=0,yr=0,iocfg=7,mode=0):
    """dtvtrans command: CMD_SYS
    Return result
    """
    (lo,hi) = self.lohi(ptr)
    cmd = "c0400%02x%02x%02x%02x%02x%02x%02x%02x" % (mode,lo,hi,sr,acc,xr,yr,iocfg)
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result
    return self.cmdline.get_status_byte()

  def sys_result(self,mode=0):
    """dtvtrans command: CMD_SYS_RESULT
    Return (result,sr,acc,xr,yr)
    """
    cmd = "c0504%02x" % mode
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return (result,0,0,0,0)
    (result,output) = self.cmdline.get_output_bytes(4)
    if result != STATUS_OK:
      return (result,0,0,0,0)
    return (STATUS_OK,output[0],output[1],output[2],output[3])

  def sys_call(self,ptr,sr=0,acc=0,xr=0,yr=0,iocfg=7,timeout=10.0,mode=0):
    """perform a sys call and wait for result
    Return (result,sr,acc,xr,yr,duration)
    """

    # do sys
    result = self.sys(ptr,sr,acc,xr,yr,iocfg,mode=mode)
    if result != STATUS_OK:
      return (result,0,0,0,0,0)

    # check for presence again
    start_time = time.time()
    result = self.is_alive(timeout)
    end_time = time.time()
    duration = end_time - start_time
    if result != STATUS_OK:
      return (result,0,0,0,0,duration)

    # fetch result
    (result,sr,acc,xr,yr) = self.sys_result(mode=mode)
    return (result,sr,acc,xr,yr,duration)

  def query_revision(self):
    """dtvtrans command: CMD_QUERY_REVISION
    Return (result,major,minor)
    """
    cmd = "c8002"
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return (result,0,0)
    (result,output) = self.cmdline.get_output_bytes(2)
    if result != STATUS_OK:
      return (result,0,0)
    major = output[0]
    minor = output[1]
    if major == 0xff:
      major = 0
      minor = 0
    return (STATUS_OK,major,minor)

  def query_revision_string(self):
    """dtvtrans command: CMD_QUERY_REVISION
    Return (result,revision)
    """
    (result,major,minor) = self.query_revision()
    if result != STATUS_OK:
      return result,"?.?"
    if major == 0:
      return result,"pre1.0"
    else:
      return result,"%d.%d" % (major,minor)

  def query_implementation(self):
    """dtvtrans command: CMD_QUERY_IMPLEMENTATION
    Return (result,impl)
    """
    cmd = "c81ff"
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return (result,"")
    (result,output) = self.cmdline.get_var_output_bytes()
    if result != STATUS_OK:
      return (result,"")
    impl = ""
    for v in output:
      impl += chr(v)
    return (result,impl)

  def query_config(self):
    """dtvtrans command: CMD_QUERY_CONFIG
    Return (result,port,mode,start,end)
    """
    cmd = "c8208"
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return (result,0,0,0,0)
    (result,output) = self.cmdline.get_output_bytes(8)
    if result != STATUS_OK:
      return (result,0,0,0,0)
    port  = output[0]
    mode  = output[1]
    start = output[2] | (output[3]<<8) | (output[4]<<16)
    end   = output[5] | (output[6]<<8) | (output[7]<<16)
    if port > 2:
      return (CLIENT_ERROR_INVALID_HEX_NUMBER,0,0,0,0)
    if mode > 1:
      return (CLIENT_ERROR_INVALID_HEX_NUMBER,0,0,0,0)
    return (STATUS_OK,port,mode,start,end)

  def set_blockctrl(self,flags):
    """dtvtrans command: CMD_SET_BLOCKCTL
    Return result
    """
    cmd = "c8300%02x" % flags
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result
    return self.cmdline.get_status_byte()

  def init(self,mode=INIT_FULL_KERNAL):
    """dtvtrans command: CMD_INIT
    Returns result
    """
    cmd = "c4000%02x" % mode
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result
    return self.cmdline.get_status_byte()

  def load(self,mode=LOAD_NORMAL):
    """dtvtrans command: CMD_LOAD
    Returns result
    """
    cmd = "c4100%02x" % mode
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result
    return self.cmdline.get_status_byte()

  def run(self,mode=RUN_NORMAL):
    """dtvtrans command: CMD_RUN
    Returns result
    """
    cmd = "c4200%02x" % mode
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result
    return self.cmdline.get_status_byte()

  def exit(self,mode=EXIT_NORMAL):
    """dtvtrans command: CMD_EXIT
    Returns result
    """
    cmd = "c4300%02x" % mode
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result
    return self.cmdline.get_status_byte()

  def do_print_short(self,text):
    """dtvtrans command: CMD_PRINT
    Returns result
    """
    cmd = "c6000%02x" % len(text)
    for t in text:
      cmd += "%02x" % ord(t)
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result
    return self.cmdline.get_status_byte()

  def do_print(self,text):
    """Print larger blocks by sending small print commands
    Return result
    """
    l=len(text)
    if l<=10:
      return self.do_print_short(text)
    else:
      t1=text[0:10]
      status = self.do_print_short(t1)
      if status != STATUS_OK:
        return status
      t2=text[10:]
      return self.do_print(t2)

  def color(self,border,back,fore):
    """dtvtrans command: CMD_COLOR
    Returns result
    """
    cmd = "c61%02x%02x%02x" % (border,back,fore)
    result = self.cmdline.do_command(cmd)
    if result != STATUS_OK:
      return result
    return self.cmdline.get_status_byte()

  # ----- joystick ----------------------------------------------------------

  def joy_wiggle(self,duration,delay,callback=lambda x:True):
    """Wiggle joystick to enter command prompt in intro"""
    stream = self.joyStream.generate_wiggle_stream(duration,delay)
    print "\t%d seconds of wiggling with %d ms delay" % (duration,delay*10)
    print "\tsending joy stream with %d bytes" % len(stream)
    return self.transfer.do_joy_stream(stream,callback)

  def joy_rawkey(self,delta,delay,callback=lambda x:True):
    """Press a single key on the virtual DTV keyboard by specifying the
       delta move"""
    stream = self.joyStream.generate_delta_move_stream(delta,delay)
    print "\tpressing raw key at",delta,"with",delay*10,"ms delay"
    print "\tsending joy stream with %d bytes" % len(stream)
    return self.transfer.do_joy_stream(stream,callback)

  def joy_stream(self,string,
                 joy_delay=0,
                 verbose=False,
                 test_mode=False,
                 callback=lambda x:True):
    """Execute a joy stream given in string notation"""
    if joy_delay == 0:
      joy_delay = 6
    js_seq,total = self.joyStream.parse_string_stream_seq(string,joy_delay)
    print "\tjoy string: converted string with %d bytes and %d ms start delay" % (len(string),joy_delay*10)
    print "\tjoy stream: sending stream with %d segments and %d bytes" % (len(js_seq),total)
    if verbose:
      print "\tdump:",self.joyStream.dump_stream_seq(js_seq)
    if test_mode:
      return STATUS_OK,0
    else:
      return self.transfer.do_joy_stream_seq(js_seq,callback)

  def joy_type(self,string,
               screen_code=False,
               type_delay=0,
               joy_delay=0,
               start_key='',
               verbose=False,
               test_mode=False,
               callback=lambda x:True):
    """Type a string on the virtual DTV keyboard"""

    # set auto type defaults
    status=self.autoType.setup(start_key,type_delay,joy_delay)
    if status != STATUS_OK:
      return status

    # conver string from auto type
    if screen_code:
      sc = ScreenCode(verbose,self.autoType,self.joyStream)
      at_string = sc.convert_binary_to_type_string(string)
      print "\tscreen code: converting %d bytes to %d auto type string bytes" % (len(string),len(at_string))
      if verbose:
        print "\tdump:",at_string
      string = at_string

    at_seq=self.autoType.convert_string_to_autotype_seq(string)
    print "\tauto type:  typing %d joy string bytes with %d sequence entries" % (len(string),len(at_seq))
    js_seq,total_cmds = self.joyStream.convert_autotype_seq(at_seq)
    print "\tjoy stream: sending stream with %d segment(s) and %d total bytes" % (len(js_seq),total_cmds)
    if verbose:
      print "\test. duration:",self.joyStream.estimate_stream_seq_duration(js_seq)
      print "\tjoy str. dump:",self.joyStream.dump_stream_seq(js_seq)
    if test_mode:
      return STATUS_OK,0
    else:
      return self.transfer.do_joy_stream_seq(js_seq,callback)

  # ----- diagnose commands -------------------------------------------------

  def diagnose_read_memory_only_dtv(self,rom,start,length,callback=lambda x:True,pattern=0,block_size=0x400):
    """Read a memory block from the DTV but do not receive the data via serial.
    Return (result,stat).
    """
    if pattern != self.transfer.get_diagnose_pattern():
      result = self.transfer.set_diagnose_pattern(pattern)
      if result != STATUS_OK:
        return result

    cmd = "r%02x%06x%06x" % (rom,start,length)
    self.transfer.begin_rx_rates()
    result = self.transfer.do_diagnose_command_only_dtv(cmd,length,False,callback=callback,block_size=block_size)
    stat = self.transfer.get_rx_rates(length)
    return (result,stat)

  def diagnose_write_memory_only_dtv(self,rom,start,length,callback=lambda x:True,pattern=0,block_size=0x400):
    """Write a memory block to the DTV but do not send the data via serial.
    Return (result,stat).
    """
    if pattern != self.transfer.get_diagnose_pattern():
      result = self.transfer.set_diagnose_pattern(pattern)
      if result != STATUS_OK:
        return result

    cmd = "w%02x%06x%06x" % (rom,start,length)
    self.transfer.begin_tx_rates()
    result = self.transfer.do_diagnose_command_only_dtv(cmd,length,True,callback=callback,block_size=block_size)
    stat = self.transfer.get_tx_rates(length)
    return (result,stat)

  def diagnose_read_memory_only_client(self,length,callback=lambda x:True,pattern=0,block_size=0x400):
    """Read a memory block from the dtv2ser device but do not transfer from DTV.
    Return (result,stat).
    """
    if pattern != self.transfer.get_diagnose_pattern():
      result = self.transfer.set_diagnose_pattern(pattern)
      if result != STATUS_OK:
        return result

    cmd = "r00000000%06x" % length
    self.transfer.begin_rx_rates()
    result = self.transfer.do_diagnose_receive_command_only_client(cmd,0,length,callback=callback,block_size=block_size)
    stat = self.transfer.get_rx_rates(length)
    return (result,stat)

  def diagnose_write_memory_only_client(self,length,callback=lambda x:True,pattern=0,block_size=0x400):
    """Write a memory block to the dtv2ser device but do not transfer to the DTV.
    Return (result,stat).
    """
    if pattern != self.transfer.get_diagnose_pattern():
      result = self.transfer.set_diagnose_pattern(pattern)
      if result != STATUS_OK:
        return result

    cmd = "w00000000%06x" % length
    self.transfer.begin_tx_rates()
    result = self.transfer.do_diagnose_send_command_only_client(cmd,0,length,callback=callback,block_size=block_size)
    stat = self.transfer.get_tx_rates(length)
    return (result,stat)

  # ----- high level commands -----------------------------------------------

  def read_word(self,addr):
    """Read a word form memory in lo hi format
    Return (result,value)
    """
    (result,data,stat) = self.read_memory(0,addr,2)
    if result != STATUS_OK:
      return (result,0)
    value = ord(data[0]) | (ord(data[1])<<8)
    return (STATUS_OK,value)

  def write_word(self,addr,val):
    """Read a word form memory in lo hi format
    Return result
    """
    data = chr(val & 0xff) + chr((val >> 8) & 0xff)
    (result,stat) = self.write_memory(0,addr,data)
    return result

  def read_byte(self,addr):
    """Read a byte form memory
    Return (result,value)
    """
    (result,data,stat) = self.read_memory(0,addr,1)
    if result != STATUS_OK:
      return (result,0)
    value = ord(data[0])
    return (STATUS_OK,value)

  def write_byte(self,addr,val):
    """Write a byte to memory
    Return result
    """
    data = chr(val & 0xff)
    (result,stat) = self.write_memory(0,addr,data)
    return result

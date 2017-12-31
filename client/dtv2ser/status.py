#
# status.py - status constants
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

STATUS_OK = 0

# command line error codes
CMDLINE_ERROR_LINE_TOO_LONG        = 0x101
CMDLINE_ERROR_UNKNOWN_COMMAND      = 0x102
CMDLINE_ERROR_NO_ARGS_ALLOWED      = 0x103
CMDLINE_ERROR_TOO_FEW_ARGS         = 0x104
CMDLINE_ERROR_ARG_TOO_SHORT        = 0x105
CMDLINE_ERROR_NO_HEX_ARG           = 0x106
CMDLINE_ERROR_TOO_MANY_ARGS        = 0x107
# add this flag to command line errors to distinguish them from transfer errors
CMDLINE_ERROR_MASK                 = 0x100

# transfer error codes
TRANSFER_ERROR_DTVLOW_NOACK1       = 0x201
TRANSFER_ERROR_DTVLOW_NOACK2       = 0x202
TRANSFER_ERROR_DTVLOW_NOACK3       = 0x203
TRANSFER_ERROR_DTVLOW_NOACK4       = 0x204
TRANSFER_ERROR_DTVLOW_BEGIN        = 0x205
TRANSFER_ERROR_DTVTRANS_CHECKSUM   = 0x206
TRANSFER_ERROR_CLIENT_TIMEOUT      = 0x207
TRANSFER_ERROR_VERIFY_MISMATCH     = 0x208
TRANSFER_ERROR_CLIENT_ABORT        = 0x209
TRANSFER_ERROR_CRC16_MISMATCH      = 0x20a
TRANSFER_ERROR_COMMAND             = 0x20b
TRANSFER_ERROR_NOT_ALIVE           = 0x20c

# mask for transfer result
TRANSFER_ERROR_MASK                = 0x200

# parameter error codes
PARAMETER_ERROR_EEPROM_NOT_READY   = 0x301
PARAMETER_ERROR_EEPROM_CRC_MISMATCH= 0x302
# mask for parameter errors
PARAMETER_ERROR_MASK               = 0x300

# client error codes
CLIENT_ERROR_SERVER_NOT_READY      = 0x401
CLIENT_ERROR_SERVER_TIMEOUT        = 0x402
CLIENT_ERROR_CRC16_MISMATCH        = 0x403
CLIENT_ERROR_PARAM_SIZE_MISMATCH   = 0x404
CLIENT_ERROR_INVALID_BASIC_RANGE   = 0x405
CLIENT_ERROR_INVALID_HEX_NUMBER    = 0x406
CLIENT_ERROR_CORRUPT_SERIAL_DATA   = 0x407
CLIENT_ERROR_FILE_ERROR            = 0x408
CLIENT_ERROR_INVALID_ARGUMENT      = 0x409
# mask for client errors
CLIENT_ERROR_MASK                  = 0x400

# ----- result name -----
result_name = {
  STATUS_OK                          : 'OK',
  # command line error codes
  CMDLINE_ERROR_LINE_TOO_LONG        : 'Command Line: Line too long',
  CMDLINE_ERROR_UNKNOWN_COMMAND      : 'Command Line: Unknown Command',
  CMDLINE_ERROR_NO_ARGS_ALLOWED      : 'Command Line: No Arguments allowed',
  CMDLINE_ERROR_TOO_FEW_ARGS         : 'Command Line: Too few Arguments',
  CMDLINE_ERROR_ARG_TOO_SHORT        : 'Command Line: Argument too short',
  CMDLINE_ERROR_NO_HEX_ARG           : 'Command Line: No Hex Argument',
  CMDLINE_ERROR_TOO_MANY_ARGS        : 'Command Line: Too many Arguments',
  # transfer error codes
  TRANSFER_ERROR_DTVLOW_NOACK1       : 'Transfer: DTVlow: No Ack1',
  TRANSFER_ERROR_DTVLOW_NOACK2       : 'Transfer: DTVlow: No Ack2',
  TRANSFER_ERROR_DTVLOW_NOACK3       : 'Transfer: DTVlow: No Ack3',
  TRANSFER_ERROR_DTVLOW_NOACK4       : 'Transfer: DTVlow: No Ack4',
  TRANSFER_ERROR_DTVLOW_BEGIN        : 'Transfer: DTVlow: Invalid Begin',
  TRANSFER_ERROR_DTVTRANS_CHECKSUM   : 'Transfer: DTVtrans: Checksum Error',
  TRANSFER_ERROR_CLIENT_TIMEOUT      : 'Transfer: Client Timeout',
  TRANSFER_ERROR_VERIFY_MISMATCH     : 'Transfer: Verify Mismatch',
  TRANSFER_ERROR_CLIENT_ABORT        : 'Transfer: Client aborted',
  TRANSFER_ERROR_CRC16_MISMATCH      : 'Transfer: CRC16 Mismatch',
  TRANSFER_ERROR_COMMAND             : 'Transfer: Command Error',
  TRANSFER_ERROR_NOT_ALIVE           : 'Transfer: Server is not alive',
  # parameter error codes
  PARAMETER_ERROR_EEPROM_NOT_READY   : 'Parameter: EEPROM not ready',
  PARAMETER_ERROR_EEPROM_CRC_MISMATCH: 'Parameter: EEPROM CRC mismatch',
  # client error codes
  CLIENT_ERROR_SERVER_NOT_READY      : 'Client: Server not ready',
  CLIENT_ERROR_SERVER_TIMEOUT        : 'Client: Server timed out',
  CLIENT_ERROR_CRC16_MISMATCH        : 'Client: Transfer CRC16 mismatch',
  CLIENT_ERROR_PARAM_SIZE_MISMATCH   : 'Client: Parameter size mismatch',
  CLIENT_ERROR_INVALID_BASIC_RANGE   : 'Client: Invalid Basic range',
  CLIENT_ERROR_INVALID_HEX_NUMBER    : 'Client: Invalid Hex number',
  CLIENT_ERROR_CORRUPT_SERIAL_DATA   : 'Client: Corrupt serial data',
  CLIENT_ERROR_FILE_ERROR            : 'Client: File Error',
  CLIENT_ERROR_INVALID_ARGUMENT      : 'Client: Invalid Argument'
}

# ----- parameters -----

# byte parameters:
PARAM_BYTE_DTVLOW_RECV_DELAY           = 0
PARAM_BYTE_ERROR_CONDITION_LOOPS       = 1
PARAM_BYTE_DIAGNOSE_PATTERN            = 2
PARAM_BYTE_IS_ALIVE_REPEAT             = 3
PARAM_BYTE_IS_ALIVE_DELAY              = 4
PARAM_BYTE_MAX                         = 5
# word parameters:
PARAM_WORD_DTVLOW_WAIT_FOR_ACK_DELAY   = 0
PARAM_WORD_DTVLOW_PREPARE_RESET_DELAY  = 1
PARAM_WORD_DTVLOW_RESET_DELAY          = 2
PARAM_WORD_ERROR_CONDITION_DELAY       = 3
PARAM_WORD_SERIAL_RTS_TIMEOUT          = 4
PARAM_WORD_SERIAL_READ_AVAIL_TIMEOUT   = 5
PARAM_WORD_SERIAL_SEND_READY_TIMEOUT   = 6
PARAM_WORD_DTV_TRANSFER_BLOCK_SIZE     = 7
PARAM_WORD_IS_ALIVE_IDLE               = 8
PARAM_WORD_MAX                         = 9

# parameter descriptions
param_byte_name = (
  'DTVlow: Receive Delay       (~200ns)',   # 0
  'Error Condition: Loops      (counter)',  # 1
  'Diagnose: Byte Pattern',                 # 2
  'Is Alive: Stable Repeat     (counter)',  # 3
  'Is Alive: Stable Delay      (ms)'     # 4
)
param_word_name = (
  'DTVlow: Wait For Ack        (ms)',    # 0
  'DTVlow: Reset Prepare Delay (ms)',    # 1
  'DTVlow: Reset Delay         (ms)',     # 2
  'Error Condition: Delay      (ms)',     # 3
  'Serial: RTS Timeout         (ms)',    # 4
  'Serial: Read avail Timeout  (ms)',    # 5
  'Serial: Write ready Timeout (ms)',    # 6
  'Transfer: DTV Block Size    (bytes)',    # 7
  'Is Alive: Idle Delay        (ms)'     # 8
)

def get_result_string(result):
  """Get a string for a result code."""
  if result_name.has_key(result):
    return result_name[result]
  else:
    return "UNKNOWN ERROR"

# ----- reset mode -----

RESET_NORMAL          = 0x00
RESET_ENTER_DTVTRANS  = 0x01
RESET_BYPASS_DTVMON   = 0x02

# ----- joystick -----

JOY_MASK              = 0x1f
JOY_FIRE              = 0x10
JOY_UP                = 0x01
JOY_DOWN              = 0x02
JOY_LEFT              = 0x04
JOY_RIGHT             = 0x08
JOY_NONE              = 0x00

JOY_COMMAND_MASK      = 0xe0
JOY_COMMAND_EXIT      = 0x80
JOY_COMMAND_WAIT      = 0x20
JOY_COMMAND_OUT       = 0x00

# ----- autotype -----

AutoType_DeltaMove   = 0
AutoType_JoyStream   = 1

# ----- joystream -----

JoyStream_Commands   = 0
JoyStream_Sleep      = 1
JoyStream_PulseDelay = 2

# ----- Transfer Mode -----

TRANSFER_MODE_NORMAL      = 0
TRANSFER_MODE_SERIAL_ONLY = 1
TRANSFER_MODE_DTV_ONLY    = 2

# ===== DTVTRANS =====

INIT_FULL_BASIC     = 0x00
INIT_MINIMAL_BASIC  = 0x01
INIT_FULL_KERNAL    = 0x02
INIT_MINIMAL_KERNAL = 0x03

init_mode_text = (
"full BASIC",
"minimal BASIC",
"full KERNAL",
"minimal KERNAL"
)

LOAD_NORMAL         = 0x00
LOAD_NO_RELINK      = 0x01

RUN_NORMAL          = 0x00

EXIT_NORMAL         = 0x00
EXIT_ONLY_EXIT      = 0x01

# ----- Strings -----

string_cursor = "\x12 \x92"
string_no_cursor = "\x9d \x9d"
string_ready = "\rREADY.\r" + string_cursor

string_init_screen = \
  "\r    **** COMMODORE 64 BASIC V2 ****\r\r" + \
  " 64K RAM SYSTEM  38911 BASIC BYTES FREE\r" + \
  string_ready

string_load = string_no_cursor + \
  "LOAD\"REMOTE\",8,1\r\rSEARCHING FOR REMOTE\rLOADING" + \
  string_ready

string_save = string_no_cursor + \
  "SAVE\"REMOTE\",8\r\rSAVING REMOTE"+ \
  string_ready

string_run = string_no_cursor + "RUN\r"




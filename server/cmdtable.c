/*
 * cmdtable.c - table of commands
 *
 * Written by
 *  Christian Vogelgsang <chris@vogelgsang.org>
 *
 * This file is part of dtv2ser.
 * See README for copyright notice.
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 *  02111-1307  USA.
 *
 */

#include <stdint.h>

#include "board.h"

#include "cmdtable.h"

#include "command.h"
#include "paramcmd.h"
#include "transfercmd.h"
#include "joycmd.h"
#include "boot.h"

// ---------- The Command Table ---------------------------------------------
command_t command_table[] = {
  // transfer commands
  COMMAND("m","b",exec_transfer_mode),
  COMMAND("r","btt",exec_read_memory),
  COMMAND("w","btt",exec_write_memory),
  COMMAND("t",0,exec_transfer_result),
#ifdef USE_BOOT
  COMMAND("b","ww",exec_boot_memory),
#endif

  // dtvtrans commands
  COMMAND("a","w",exec_is_alive),
  COMMAND("c","bb*",exec_command),
#ifdef USE_OLDCMD
  COMMAND("g","w",exec_go_memory),
#endif

  // dtv2ser commands
  COMMAND("x","b",exec_reset_dtv),
  COMMAND("v",0,exec_version),
#ifdef USE_JOYSTICK
  COMMAND("j",0,exec_joy_stream),
#endif

  // preset commands
  COMMAND("pbs","bb",exec_set_byte_param),
  COMMAND("pbg","b",exec_get_byte_param),
  COMMAND("pws","bw",exec_set_word_param),
  COMMAND("pwg","b",exec_get_word_param),
  COMMAND("pc","b",exec_param_cmd),
  COMMAND("pq",0,exec_param_query),

  // block commands
#ifdef USE_BLOCKCMD
  COMMAND("dbr","bbww",exec_block_read_memory),
  COMMAND("dbw","bbww",exec_block_write_memory),
#endif

  END_OF_COMMAND
};


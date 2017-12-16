/*
 * cmdline.h - command line input handling
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

#ifndef CMDLINE_H
#define CMDLINE_H

#include "global.h"

// max number of chars in a command line
#define CMDLINE_SIZE 40

// command status
#define CMDLINE_STATUS_OK               0x00
#define CMDLINE_ERROR_LINE_TOO_LONG     0x01
#define CMDLINE_ERROR_UNKNOWN_COMMAND   0x02
#define CMDLINE_ERROR_NO_ARGS_ALLOWED   0x03
#define CMDLINE_ERROR_TOO_FEW_ARGS      0x04
#define CMDLINE_ERROR_ARG_TOO_SHORT     0x05
#define CMDLINE_ERROR_NO_HEX_ARG        0x06
#define CMDLINE_ERROR_TOO_MANY_ARGS     0x07

// define max number of arguments of the given type that occur in a single command
#define CMDLINE_MAX_ARG_BYTE    16
#define CMDLINE_MAX_ARG_WORD    2
#define CMDLINE_MAX_ARG_DWORD   2

// container for all arguments passed to a command
typedef struct {
  uint8_t arg_byte[CMDLINE_MAX_ARG_BYTE];
  uint16_t arg_word[CMDLINE_MAX_ARG_WORD];
  uint32_t arg_dword[CMDLINE_MAX_ARG_DWORD];
  uint8_t num_byte;
  uint8_t num_word;
  uint8_t num_dword;
} cmdline_args_t;

// access the global command line args
extern cmdline_args_t cmdline_args;

// access the command line arguments
#define CMDLINE_ARG_BYTE(x)  (cmdline_args.arg_byte[x])
#define CMDLINE_ARG_WORD(x)  (cmdline_args.arg_word[x])
#define CMDLINE_ARG_DWORD(x) (cmdline_args.arg_dword[x])

#define CMDLINE_NUM_ARG_BYTE (cmdline_args.num_byte)

// structure to define a command
typedef struct {
  uint8_t    len;             // length of command string
  uint8_t   *name;            // e.g.  "r"
  uint8_t   *args_pattern;    // use a sequence of b=byte,w=word,t=tribyte
  void (*execute_cmd)(void); // execute command
} command_t;

#define COMMAND(name,pattern,execute) \
{ sizeof(name)-1,(uint8_t*)name,(uint8_t*)pattern,execute }
#define END_OF_COMMAND { 0,0,0,0 }

// call this initially to setup the command line on startup
extern void cmdline_init(void);

// call this regua
extern void cmdline_handle(void);

#endif

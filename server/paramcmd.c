/*
 * paramcmd.c - handle parameter commands
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

#include "command.h"

#include "uart.h"
#include "uartutil.h"
#include "param.h"
#include "paramcmd.h"

void exec_set_byte_param(void)
{
  PARAM_BYTE(CMDLINE_ARG_BYTE(0)) = CMDLINE_ARG_BYTE(1);
  uart_send_hex_byte_crlf(0);
}

void exec_get_byte_param(void)
{
  uint8_t value = PARAM_BYTE(CMDLINE_ARG_BYTE(0));
  uart_send_hex_byte_crlf(value);
}

void exec_set_word_param(void)
{
  PARAM_WORD(CMDLINE_ARG_BYTE(0)) = CMDLINE_ARG_WORD(0);
  uart_send_hex_byte_crlf(0);
}

void exec_get_word_param(void)
{
  uint16_t value = PARAM_WORD(CMDLINE_ARG_BYTE(0));
  uart_send_hex_word_crlf(value);
}

void exec_param_cmd(void)
{
  uint8_t mode = CMDLINE_ARG_BYTE(0);
  uint8_t result = PARAM_OK;
  if(mode==PARAM_COMMAND_RESET)
    param_reset();
  else if(mode==PARAM_COMMAND_LOAD)
    result = param_load();
  else
    result = param_save();
  uart_send_hex_byte_crlf(result);
}

void exec_param_query(void)
{
  uart_send_hex_byte_crlf(PARAM_BYTE_MAX);
  uart_send_hex_byte_crlf(PARAM_WORD_MAX);
}

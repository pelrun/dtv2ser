/*
 * uartutil.c - serial utility routines
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

#include "uart.h"
#include "util.h"

uint8_t uart_send_string(uint8_t *str)
{
  while(*str) {
    if(!uart_send(*str))
      return 0;
    str++;
  }
  return 1;
}

uint8_t uart_send_data(uint8_t *data,uint8_t len)
{
  for(uint8_t i=0;i<len;i++) {
    if(!uart_send(data[i]))
      return 0;
  }
  return 1;
}

uint8_t uart_send_crlf(void)
{
  return uart_send_string((uint8_t *)"\r\n");
}

static uint8_t buf[6];

uint8_t uart_send_hex_byte_crlf(uint8_t data)
{
  byte_to_hex(data,buf);
  if(uart_send_data(buf,2))
    return uart_send_crlf();
  else
    return 0;
}

uint8_t uart_send_hex_word_crlf(uint16_t data)
{
  word_to_hex(data,buf);
  if(uart_send_data(buf,4))
    return uart_send_crlf();
  else
    return 0;
}

uint8_t uart_send_hex_dword6_crlf(uint32_t data)
{
  dword_to_hex6(data,buf);
  if(uart_send_data(buf,6))
    return uart_send_crlf();
  else
    return 0;
}


/*
 * uartutil.h - serial utility routines
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

#ifndef UARTUTIL_H
#define UARTUTIL_H

// send a c string
uint8_t uart_send_string(uint8_t *data);
// send data
uint8_t uart_send_data(uint8_t *data,uint8_t size);
// send a CR+LF
uint8_t uart_send_crlf(void);

// send a hex byte
uint8_t uart_send_hex_byte_crlf(uint8_t data);
// send a hex word
uint8_t uart_send_hex_word_crlf(uint16_t data);
// send a hex6 dword
uint8_t uart_send_hex_dword6_crlf(uint32_t data);

#endif


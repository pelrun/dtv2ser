/*
 * uart.h - serial hw routines
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

#ifndef UART_H
#define UART_H

// init uart and rts/cts
void uart_init(void);

// is rx data available?
uint8_t uart_read_data_available(void);

// stop reception (clear CTS)
void uart_stop_reception(void);

// allow reception (clear read buffer and set CTS)
void uart_start_reception(void);

// read a byte (from buffer) (with cts handshaking)
uint8_t uart_read(uint8_t *data);

// write a byte (with rts handshaking)
uint8_t uart_send(uint8_t data);

#endif

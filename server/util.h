/*
 * util.h - utilities
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

#ifndef UTIL_H
#define UTIL_H

// ----- conversion functions -----
// convert nybble to hex char
extern uint8_t nybble_to_hex(uint8_t in);
// convert uint8_t to 2 hex chars
extern void byte_to_hex(uint8_t in,uint8_t *out);
// convert word to 4 hex chars
extern void word_to_hex(uint16_t in,uint8_t *out);
// convert dword to 6 hex chars
extern void dword_to_hex6(uint32_t in,uint8_t *out);

// ----- parse functions: 01=ok, 00=error -----
// parse a nybble
extern uint8_t parse_nybble(uint8_t in,uint8_t *value);
// parse a byte
extern uint8_t parse_byte(uint8_t *str,uint8_t *value);
// parse a word
extern uint8_t parse_word(uint8_t *str,uint16_t *value);
// parse a 6 byte dword
extern uint8_t parse_dword6(uint8_t *str,uint32_t *value);

#endif


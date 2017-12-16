/*
 * util.c - utilities
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

#include "util.h"

// convert to hex

uint8_t nybble_to_hex(uint8_t in)
{
  if(in<10)
    return '0' + in;
  else
    return 'A' + in - 10;
}

void byte_to_hex(uint8_t in,uint8_t *out)
{
  out[0] = nybble_to_hex(in >> 4);
  out[1] = nybble_to_hex(in & 0xf);
}

void word_to_hex(uint16_t in,uint8_t *out)
{
  byte_to_hex((uint8_t)(in>>8),out);
  byte_to_hex((uint8_t)(in&0xff),out+2);
}

void dword_to_hex6(uint32_t addr,uint8_t *out)
{
  byte_to_hex((uint8_t)(addr>>16),out);
  word_to_hex((uint16_t)(addr&0xffff),out+2);
}

// parse

uint8_t parse_nybble(uint8_t c,uint8_t *value)
{
  if((c>='a')&&(c<='f')) {
    *value = c + 10 - 'a';
    return 1;
  }
  else if((c>='A')&&(c<='F')) {
    *value = c + 10 - 'A';
    return 1;
  }
  else if((c>='0')&&(c<='9')) {
    *value = c - '0';
    return 1;
  }
  else
    return 0;
}

uint8_t parse_byte(uint8_t *str,uint8_t *value)
{
  uint8_t val;
  if(!parse_nybble(str[0],&val))
    return 0;
  val <<= 4;
  if(!parse_nybble(str[1],value))
    return 0;
  *value |= val;
  return 1;
}

uint8_t parse_word(uint8_t *str,uint16_t *value)
{
  uint8_t val;
  if(!parse_byte(&str[0],&val))
    return 0;
  uint8_t val2;
  if(!parse_byte(&str[2],&val2))
    return 0;
  *value = (uint16_t)val << 8 | val2;
  return 1;
}

uint8_t parse_dword6(uint8_t *str,uint32_t *value)
{
  uint8_t val;
  if(!parse_byte(&str[0],&val))
    return 0;
  uint8_t val2;
  if(!parse_byte(&str[2],&val2))
    return 0;
  uint8_t val3;
  if(!parse_byte(&str[4],&val3))
    return 0;
  *value = (uint32_t)val << 16 | (uint32_t)val2 << 8 | val3;
  return 1;
}


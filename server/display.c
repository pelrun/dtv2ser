/*
 * display.c - handle output with leds and lcd
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

#include "display.h"
#include "util.h"

#ifdef USE_LCD

static u08 print_line[] = "a:xxxxxx";

void lcd_print_version(void)
{
  lcd_print_string(0,0,(u08 *)("dtv2ser " VERSION));
}

void lcd_print_string(u08 x,u08 y,u08 *string)
{
  lcd_pos(x,y);
  while(*string) {
    lcd_char(*string++);
  }
}

void lcd_print_data(u08 x,u08 y,u08 *data,u08 len)
{
  lcd_pos(x,y);
  for(u08 i=0;i<len;i++) {
    lcd_char(data[i]);
  }
}

void lcd_print_byte(u08 x,u08 y,u08 c,u08 data)
{
  byte_to_hex(data,print_line+2);
  print_line[0] = c;
  lcd_print_data(x,y,print_line,4);
}

void lcd_print_word(u08 x,u08 y,u08 c,u16 data)
{
  word_to_hex(data,print_line+2);
  print_line[0] = c;
  lcd_print_data(x,y,print_line,6);
}

void lcd_print_dword6(u08 x,u08 y,u08 c,u32 data)
{
  dword_to_hex6(data,print_line+2);
  print_line[0] = c;
  lcd_print_data(x,y,print_line,8);
}

#endif

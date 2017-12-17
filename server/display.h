/*
 * display.h - handle output with leds and lcd
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

#ifndef DISPLAY_H
#define DISPLAY_H

// you can attach an LCD for more verbose dtv2ser status output
#ifdef USE_LCD

// --- lcd convenience functions ---
// print dtv2ser version
extern void lcd_print_version(void);
// print a string at position
extern void lcd_print_string(uint8_t x,uint8_t y,uint8_t *string);
// print an amount of data
extern void lcd_print_data(uint8_t x,uint8_t y,uint8_t *string,uint8_t len);
// print a byte with c:xx
extern void lcd_print_byte(uint8_t x,uint8_t y,uint8_t c,uint8_t data);
// print a word with c:xxxx
extern void lcd_print_word(uint8_t x,uint8_t y,uint8_t c,uint16_t data);
// print a dword with c:xxxxxx
extern void lcd_print_dword6(uint8_t x,uint8_t y,uint8_t c,uint32_t data);

#endif // USE_LCD

#endif // DISPLAY_H


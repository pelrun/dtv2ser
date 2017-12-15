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

#include "global.h"

// ========== arduino2009 ===================================================

#ifdef HAVE_arduino2009

#include "arduino2009.h"

// ----- LED ----------------------------------------------------------------
// init leds
#define led_init()          ard2009_led_init()

// 1. Ready LED (green)
#define led_ready_on()      ard2009_led_on(1)
#define led_ready_off()     ard2009_led_off(1)

// 2. Error LED (red)
#define led_error_on()      ard2009_led_on(4)
#define led_error_off()     ard2009_led_off(4)

// 3. Transmit LED (yellow)
#define led_transmit_on()   ard2009_led_on(2)
#define led_transmit_off()  ard2009_led_off(2)

#endif

// ========== cvm8board =====================================================

#ifdef HAVE_cvm8board

#include "cvm8board.h"

// ----- LED ----------------------------------------------------------------
// init leds
#define led_init()          cvm8_led_init()

// 1. Ready LED (green)
#define led_ready_on()      cvm8_led_on(1)
#define led_ready_off()     cvm8_led_off(1)

// 2. Error LED (red)
#define led_error_on()      cvm8_led_on(4)
#define led_error_off()     cvm8_led_off(4)

// 3. Transmit LED (yellow)
#define led_transmit_on()   cvm8_led_on(2)
#define led_transmit_off()  cvm8_led_off(2)

#endif

// ========== ctboard =======================================================

#ifdef HAVE_ctboard

#include "ctboard.h"

// ----- LED ----------------------------------------------------------------
// init leds
#define led_init()          ct_init_keyled()

// 1. Ready LED (green)
#define led_ready_on()      ct_led_on(CT_LED_GREEN)
#define led_ready_off()     ct_led_off(CT_LED_GREEN)

// 2. Error LED (red)
#define led_error_on()      ct_led_on(CT_LED_RED)
#define led_error_off()     ct_led_off(CT_LED_RED)

// 3. Transmit LED (yellow)
#define led_transmit_on()   ct_led_on(CT_LED_YELLOW)
#define led_transmit_off()  ct_led_off(CT_LED_YELLOW)

// ----- (optional) beeper --------------------------------------------------
#ifdef USE_BEEPER

// init beeper
#define beeper_init()       ct_init_beeper()
// beep for n ms
#define beeper_beep(n)      ct_beep(n)

#endif // USE_BEEPER

// ----- (optional) LCD -----------------------------------------------------
// you can attach an LCD for more verbose dtv2ser status output
#ifdef USE_LCD

// init lcd
#define lcd_init()          ct_lcd_init()
// clear the lcd screen
#define lcd_clear()         ct_lcd_clear()
// move at pos
#define lcd_pos(x,y)        ct_lcd_pos(x,y)
// write a char
#define lcd_char(ch)        ct_lcd_char(ch)

// --- lcd convenience functions ---
// print dtv2ser version
extern void lcd_print_version(void);
// print a string at position
extern void lcd_print_string(u08 x,u08 y,u08 *string);
// print an amount of data
extern void lcd_print_data(u08 x,u08 y,u08 *string,u08 len);
// print a byte with c:xx
extern void lcd_print_byte(u08 x,u08 y,u08 c,u08 data);
// print a word with c:xxxx
extern void lcd_print_word(u08 x,u08 y,u08 c,u16 data);
// print a dword with c:xxxxxx
extern void lcd_print_dword6(u08 x,u08 y,u08 c,u32 data);

#endif // USE_LCD

#endif // DISPLAY_H

#endif // HAVE_ctboard


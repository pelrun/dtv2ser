/*
 * cvm8board.h - cvm8board hardware access
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

//
// CV's Mega 8 Board for dtv2ser
//
// LEDS:
//   PB0  Out  Busy LED
//   PB1  Out  Transmit LED
//   PB2  Out  Error LED
//
// RTS/CTS:
//   PD2  Out  CTS to Host
//   PD3  In   RTS of Host

#ifndef CVM8BOARD_H
#define CVM8BOARD_H

#include "global.h"
#include <avr/io.h>

// ----- LEDs -----
// init leds
void cvm8_led_init(void);
// set led given by mask
#define cvm8_led_on(mask)       { PORTB &= ~mask; }
// set led off
#define cvm8_led_off(mask)      { PORTB |= mask; }

// ----- RTS & CTS -----
// init rts,cts signalling
void cvm8_rts_cts_init(void);
// set cts value 1=on, 0=off
#define cvm8_set_cts(on)    { if(on) PORTD &= ~0x04; else PORTD |=  0x04; }
// read rts value 1=on, 0=off
#define cvm8_get_rts()      ((PIND & 0x08) == 0)

#endif


/*
 * arduino2009.c - arduino2009 hardware access
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
#include <avr/interrupt.h>

#include "arduino2009.h"

// Board init

void board_init(void)
{
   // disable watchdog
   cli();
   MCUSR &= ~(1<<WDRF);
   WDTCSR |= _BV(WDCE) | _BV(WDE);
   WDTCSR = 0;
   sei();
}

// LEDs are PB0..PB2

void led_init(void)
{
  DDRB  |= 0x07;
  PORTB |= 0x07;
}

// RTS & CTS

void uart_init_rts_cts(void)
{
  DDRD  |= 0x04; // PD2 is output
  PORTD |= 0x0c;
}

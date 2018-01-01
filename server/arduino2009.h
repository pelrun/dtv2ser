/*
 * arduino2009.h - arduino2009 hardware access
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

// LEDS:
//   PB0  Out  Busy LED
//   PB1  Out  Transmit LED
//   PB2  Out  Error LED
//
// RTS/CTS:
//   PD2  Out  CTS to Host (Connectecd to X3 Pad Pin 1)
//   PD3  In   RTS of Host (N/A on Arduino)

#ifndef ARDUINO2009BOARD_H
#define ARDUINO2009BOARD_H

#include <avr/io.h>

#define DTVLOW_DATA_MASK     0x07
#define DTVLOW_CLK_MASK      0x08
#define DTVLOW_DATACLK_PORT  PORTC
#define DTVLOW_DATACLK_PIN   PINC
#define DTVLOW_DATACLK_DDR   DDRC
#define DTVLOW_DATA_SHIFT    0

#define DTVLOW_ACK_MASK      0x10
#define DTVLOW_RESET_MASK    0x20
#define DTVLOW_ACKRESET_PORT PORTC
#define DTVLOW_ACKRESET_PIN  PINC
#define DTVLOW_ACKRESET_DDR  DDRC

#define JOY_PORT        PORTC
#define JOY_DDR         DDRC

// ----- BOARD -----
void board_init(void);

// ----- LEDs -----
// init leds
void led_init(void);

// set led given by mask
#define led_on(mask)       { PORTB &= ~mask; }
// set led off
#define led_off(mask)      { PORTB |= mask; }

// 1. Ready LED (green)
#define led_ready_on()      led_on(1)
#define led_ready_off()     led_off(1)

// 2. Error LED (red)
#define led_error_on()      led_on(4)
#define led_error_off()     led_off(4)

// 3. Transmit LED (yellow)
#define led_transmit_on()   led_on(2)
#define led_transmit_off()  led_off(2)


// ----- RTS & CTS -----
// init rts,cts signalling
void uart_init_rts_cts(void);
// set cts value 1=on, 0=off
#define uart_set_cts(on)    { if(on) PORTD &= ~0x04; else PORTD |=  0x04; }
// read rts value 1=on, 0=off
#define uart_get_rts()      ((PIND & 0x08) == 0)

#define uart_init_extra()

#endif


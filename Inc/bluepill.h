/*
 * bluepill.h - stm32 blue pill hardware access
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
//   PB7  Out  Busy LED
//   PB8  Out  Transmit LED
//   PB9  Out  Error LED

#ifndef BLUEPILLBOARD_H
#define BLUEPILLBOARD_H

#define JOY_PORT        PORTC
#define JOY_DDR         DDRC
#define JOY_MASK        0x1f

#define JOY_MASK_UP     0x01
#define JOY_MASK_DOWN   0x02
#define JOY_MASK_LEFT   0x04
#define JOY_MASK_RIGHT  0x08
#define JOY_MASK_FIRE   0x10

// ----- BOARD -----
void board_init(void);

// ----- LEDs -----
// init leds
void led_init(void);

// set led given by mask
#define led_on(mask) 
// set led off 
#define led_off(mask)

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
#define uart_set_cts(on)
// read rts value 1=on, 0=off
#define uart_get_rts()

#define uart_init_extra()

#endif


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

// ----- BOARD -----
void board_init(void);

// ----- LEDs -----
// init leds
void led_init(void);

// set led given by mask
void hal_led_on(uint8_t mask);
// set led off 
void hal_led_off(uint8_t mask);

// 1. Ready LED (green)
#define led_ready_on()      hal_led_on(1)
#define led_ready_off()     hal_led_off(1)

// 2. Error LED (red)
#define led_error_on()      hal_led_on(4)
#define led_error_off()     hal_led_off(4)

// 3. Transmit LED (yellow)
#define led_transmit_on()   hal_led_on(2)
#define led_transmit_off()  hal_led_off(2)

// ----- RTS & CTS -----
// init rts,cts signalling
void uart_init_rts_cts(void);
// set cts value 1=on, 0=off
#define uart_set_cts(on)
// read rts value 1=on, 0=off
#define uart_get_rts()

#define uart_init_extra()

#endif


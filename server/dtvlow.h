/*
 * dtvlow.h - low level dtvtrans protocol
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

// Implement TLR's dtvtrans protocol on the AVR
// (Low Level Bit Banging)
//
//
// Wiring (ctboard):
//
// AVR     DTVtrans        Joystick
// ---     --------        --------
// PC4     D0              Joy A1
// PC5     D1              Joy A2
// PC6     D2              Joy A3
// PC7     CLK             Joy A4
// PA2     ACK             Joy A6
// PA3     RESET DTV       Joy A9
//
// Wiring (cvm8board, arduino2009):
//
// AVR     DTVtrans        Joystick
// ---     --------        --------
// PC0     D0              Joy A1
// PC1     D1              Joy A2
// PC2     D2              Joy A3
// PC3     CLK             Joy A4
// PC4     ACK             Joy A6
// PC5     RESET DTV       Joy A9

#ifndef DTVLOW_H
#define DTVLOW_H

// reset mode
#define DTVLOW_RESET_NORMAL            0x00
#define DTVLOW_RESET_ENTER_DTVTRANS    0x01
#define DTVLOW_RESET_BYPASS_DTVMON     0x02

// ----- low level dtvtrans -----

// startup state
void dtvlow_state_init(void);

// default state (all wires off)
void dtvlow_state_off(void);

// setup state for send bytes (output:Dx,CLK,input:ACK)
void dtvlow_state_send(void);

// setup state for recv bytes (output:CLK,input:Dx,ACK)
void dtvlow_state_recv(void);

// perform a reset of the dtv. if knock=1 then enter dtvtrans
void dtvlow_reset_dtv(uint8_t mode);

// send a byte. returns true if got ack
// make sure the send state is called first!
uint8_t dtvlow_send_byte(uint8_t byte);

// recv a byte. returns true if got ack
// make sure the recv state is called first!
uint8_t dtvlow_recv_byte(uint8_t *byte);

#ifdef USE_BOOT
// send a byte in boot mode. returns true if ok
// make sure the send state is called first!
uint8_t dtvlow_send_byte_boot(uint8_t byte);
#endif

// check presence
uint8_t dtvlow_is_alive(uint16_t timeout);

#endif


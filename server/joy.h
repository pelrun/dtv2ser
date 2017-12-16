/*
 * joy.h - low level joystick control
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

#ifndef JOY_H
#define JOY_H

#include "global.h"

#ifdef USE_JOYSTICK

#if defined(HAVE_cvm8board) || defined(HAVE_arduino2009)

#define JOY_PORT        PORTC
#define JOY_DDR         DDRC
#define JOY_MASK        0x1f

#define JOY_MASK_UP     0x01
#define JOY_MASK_DOWN   0x02
#define JOY_MASK_LEFT   0x04
#define JOY_MASK_RIGHT  0x08
#define JOY_MASK_FIRE   0x10

#else

#error Unsupported Board

#endif

void joy_begin(void);
void joy_out(uint8_t value);
void joy_end(void);

#endif

#endif


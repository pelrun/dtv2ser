/*
 * joy.c - low level joystick control
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

#include "joy.h"

#include <avr/io.h>

#ifdef USE_JOYSTICK

void joy_begin(void)
{
  JOY_PORT |= JOY_MASK;
  JOY_DDR  |= JOY_MASK;
}

void joy_out(u08 value)
{
  JOY_PORT = (~value & JOY_MASK) | ~(JOY_MASK);
}

void joy_end(void)
{
  JOY_PORT |=   JOY_MASK;
  JOY_DDR  &= ~(JOY_MASK);
}

#endif

/*
 * joycmd.h - joystick commands
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

#ifndef JOYCMD_H
#define JOYCMD_H

#include "hal.h"
#include "command.h"

void exec_joy_stream(void);

#define JOY_COMMAND_MASK    0xe0

#define JOY_COMMAND_EXIT    0x80
#define JOY_COMMAND_WAIT    0x20
#define JOY_COMMAND_OUT     0x00

#define JOY_COMMAND_OK      0
#define JOY_COMMAND_ERROR   1

#endif

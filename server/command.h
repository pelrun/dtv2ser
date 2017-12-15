/*
 * command.h - command handling
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

#ifndef COMMAND_H
#define COMMAND_H

#include "cmdline.h"

#ifdef USE_OLDCMD
//! execute memory
void exec_go_memory(void);
#endif

//! reset dtv
void exec_reset_dtv(void);
//! version
void exec_version(void);

//! execute generic command
void exec_command(void);

//! exec is alive
void exec_is_alive(void);

// signal error condition
void error_condition(void);

#endif

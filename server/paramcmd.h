/*
 * paramcmd.h - parameter command handling
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

#ifndef PARAMCMD_H
#define PARAMCMD_H

#include "command.h"

#define PARAM_COMMAND_RESET     0
#define PARAM_COMMAND_LOAD      1
#define PARAM_COMMAND_SAVE      2

void exec_set_byte_param(void);
void exec_get_byte_param(void);
void exec_set_word_param(void);
void exec_get_word_param(void);
void exec_param_cmd(void);
void exec_param_query(void);

#endif

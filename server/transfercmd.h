/*
 * transfercmd.h - transfer command handling
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

#ifndef TRANSFERCMD_H
#define TRANSFERCMD_H

#include "command.h"

// ----- transfer mode -----
// constants for the transfer mode
#define TRANSFER_MODE_NORMAL        0
#define TRANSFER_MODE_SERIAL_ONLY   1
#define TRANSFER_MODE_DTV_ONLY      2

void exec_read_memory(void);
void exec_write_memory(void);

void exec_transfer_result(void);
void exec_transfer_mode(void);

#ifdef USE_BLOCKCMD

void exec_block_read_memory(void);
void exec_block_write_memory(void);

#endif // USE_BLOCKCMD

#endif

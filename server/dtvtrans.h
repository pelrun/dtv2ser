/*
 * dtvtrans.h - high level dtvtrans protocol
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

#ifndef DTVTRANS_H
#define DTVTRANS_H

#include "transfer.h"

// receive mem block from dtv. returns status
u08 dtvtrans_recv_mem_block(void);

// send a mem block to dtv. returns status
u08 dtvtrans_send_mem_block(void);

#ifdef USE_OLDCMD
// execute mem. returns status
u08 dtvtrans_exec_mem(u16 addr);
#endif

// this special out_size reads the output length from the command
#define DTVTRANS_CMD_VARARG 0xff

// do a generic dtvtrans command

// if out_size is set to DTVTRANS_CMD_VARARG:
//  1. read first byte: size n
//  2. read <n> bytes
u08 dtvtrans_command(u08 command,u08 in_size,u08 *in_buf,u08 out_size);

#endif


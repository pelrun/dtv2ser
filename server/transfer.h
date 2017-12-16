/*
 * transfer.h - transfer core
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

#ifndef TRANSFER_H
#define TRANSFER_H

#include "global.h"

// ----- transfer status -----
#define TRANSFER_OK                 0x00
// dtvlow errors
#define TRANSFER_ERROR_DTVLOW_NOACK1       0x01
#define TRANSFER_ERROR_DTVLOW_NOACK2       0x02
#define TRANSFER_ERROR_DTVLOW_NOACK3       0x03
#define TRANSFER_ERROR_DTVLOW_NOACK4       0x04
#define TRANSFER_ERROR_DTVLOW_BEGIN        0x05
// dtvtrans errors
#define TRANSFER_ERROR_DTVTRANS_CHECKSUM   0x06
// host transfer errors
#define TRANSFER_ERROR_CLIENT_TIMEOUT      0x07
// diagnose error
#define TRANSFER_ERROR_VERIFY_MISMATCH     0x08
// abort from client
#define TRANSFER_ERROR_CLIENT_ABORT        0x09
// block crc mismatch
#define TRANSFER_ERROR_CRC16_MISMATCH      0x0a
// command error
#define TRANSFER_ERROR_COMMAND             0x0b
// is not alive
#define TRANSFER_ERROR_NOT_ALIVE           0x0c

// ----- transfer status -----
typedef struct {
  // number of bytes transferred
  uint32_t length;
  // time in ms of full transfer
  uint16_t ms_time;
  // result of last transfer
  uint8_t result;
} transfer_state_t;

// access the transfer status
extern transfer_state_t transfer_state;

// ----- command table for host transfer -----
// byte transfer function
typedef uint8_t (*host_transfer_byte_func_t)(uint8_t *data);

// host commands: transfer blocks of memory to/from host
typedef struct {
  // begin a transfer. returns status
  uint8_t (*begin_transfer)(uint32_t length);
  // end a trasfer. returns status
  uint8_t (*end_transfer)(uint8_t lastStatus);
  // end a block
  uint8_t (*check_block)(uint16_t block_crc16);
  // transfer a byte
  host_transfer_byte_func_t transfer_byte;
} host_transfer_funcs_t;

// ----- generic dtv transfer -----
// dtv transfer state
typedef struct {
  // mode: 00=ram 01=rom
  uint8_t mode;
  // bank: addr>>14
  uint8_t bank;
  // offset: addr & 0x3fff
  uint16_t offset;
  // length: <= 0x4000
  uint16_t length;
  // out: block crc16
  uint16_t crc16;
  // out: actually transferred length
  uint16_t transfer_length;
} dtv_transfer_state_t;

// the shared instance of the dtv transfer state
extern dtv_transfer_state_t dtv_transfer_state;

// transfer a block to/from the dtv. returns result (see above)
typedef uint8_t (*dtv_transfer_block_func_t)(void);

// ----- pointers to current transfer state -----
// current host transfer funcs
extern host_transfer_funcs_t *current_host_transfer_funcs;
// current dtv transfer block func
extern dtv_transfer_block_func_t current_dtv_transfer_block_func;

// ----- main transfer -----
// transfer memory from/to host/dtv. updates transfer result (see above)
extern uint8_t transfer_mem(uint8_t mode,uint32_t base,uint32_t length,uint16_t block_size);

// transfer a single memory block only
extern uint8_t transfer_mem_block(uint8_t mode,uint8_t bank,uint16_t offset,uint16_t length);

// ----- diagnose functions -----
#ifdef USE_DIAGNOSE

// dummy send block. returns status
extern uint8_t diagnose_dtv_send_block(void);
// dummy receive block. returns status
extern uint8_t diagnose_dtv_recv_block(void);

#define DIAGNOSE_HOST_MODE_READ   0
#define DIAGNOSE_HOST_MODE_WRITE  1
// set mode for diagnose transfer: 0=read from host,1=write to host
extern uint8_t diagnose_host_mode;

// dummy host transfer funcs
extern host_transfer_funcs_t diagnose_host_transfer_funcs;

#endif // USE_DIAGNOSE

#endif

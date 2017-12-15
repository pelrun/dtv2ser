/*
 * transfer.c - transfer core
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

#include "global.h"

#include <util/crc16.h>

#include "transfer.h"
#include "display.h"
#include "util.h"
#include "timer.h"
#include "param.h"
#include "sertrans.h"

#define min(a,b) ((a<b)?(a):(b))

// the transfer state
transfer_state_t transfer_state;

// the dtv transfer state
dtv_transfer_state_t dtv_transfer_state;

// current host transfer funcs
host_transfer_funcs_t *current_host_transfer_funcs = 0;
// current dtv transfer block func
dtv_transfer_block_func_t current_dtv_transfer_block_func = 0;

// ----- main transfer loop -----

static u08 transfer_begin(u08 mode,u32 length)
{
  // reset transfer state
  transfer_state.length  = 0;
  transfer_state.ms_time = 0;
  transfer_state.result  = TRANSFER_OK;

  // begin host transfer
  u08 result = current_host_transfer_funcs->begin_transfer(length);
  if(result!=TRANSFER_OK) {
    transfer_state.result = result;
    return result;
  }

  // reset dtv state
  dtv_transfer_state.transfer_length = 0;
  dtv_transfer_state.mode = mode;

  led_transmit_on();
  return TRANSFER_OK;
}

static u08 transfer_end(u08 result,u32 total_length,u16 ms_time)
{
  led_transmit_off();

  // end host transfer
  result = current_host_transfer_funcs->end_transfer(result);

  // set transfer result
  transfer_state.length  = total_length;
  transfer_state.ms_time = ms_time;
  transfer_state.result  = result;

  return result;
}

u08 transfer_mem(u08 mode,u32 base,u32 length,u16 block_size)
{
  u08 result = transfer_begin(mode,length);
  if(result!=TRANSFER_OK)
    return result;

  // start timer
  timer_10ms = 0;

  // block copy loop
  u32 total_length = 0;
  u08 toggle = 1;
  while(length) {
    u16 offset = (u16)(base & 0x3fff);
    u16 max_len = 0x4000 - offset;
    u16 block_len = min(length,block_size);
    u16 len = min(block_len,max_len);

    dtv_transfer_state.offset = offset;
    dtv_transfer_state.bank   = (u08)(base >> 14);
    dtv_transfer_state.length = len;
    dtv_transfer_state.crc16  = 0xffff;

    // call dtv func to transfer a single block
    // (calls host_funcs transfer_byte)
    result = current_dtv_transfer_block_func();
    if(result!=TRANSFER_OK)
      break;

    // host check block
    result = current_host_transfer_funcs->check_block(dtv_transfer_state.crc16);
    if(result!=TRANSFER_OK)
      break;

    // update
    u16 transfer_length = dtv_transfer_state.transfer_length;
    base   += transfer_length;
    length -= transfer_length;
    total_length += transfer_length;

    // toggle led
    toggle = toggle^1;
    if(toggle) {
      led_transmit_on();
    } else {
      led_transmit_off();
    }

    // break if not ok
    if(result!=TRANSFER_OK)
      break;
  }

  return transfer_end(result,
                      total_length,
                      timer_10ms);
}

u08 transfer_mem_block(u08 mode,u08 bank,u16 offset,u16 length)
{
  u08 result = transfer_begin(mode,length);
  if(result!=TRANSFER_OK)
    return result;

  dtv_transfer_state.bank   = bank;
  dtv_transfer_state.offset = offset;
  dtv_transfer_state.length = length;

  // trigger a single block transfer
  result = current_dtv_transfer_block_func();

  return transfer_end(result,
                      dtv_transfer_state.transfer_length,
                      0);
}

// ----- diagnose transfer functions ----------------------------------------
#ifdef USE_DIAGNOSE

u08 diagnose_dtv_send_block(void)
{
  u08 result;
  u16 length = dtv_transfer_state.length;

  u16 pos = 0;
  u16 crc16 = dtv_transfer_state.crc16;
  while(length) {
    // transfer byte from host
    u08 data;
    result = current_host_transfer_funcs->transfer_byte(&data);
    if(result!=TRANSFER_OK)
      break;

    // update checksum
    crc16 = _crc16_update(crc16,data);

    length--;
    pos++;
  }
  dtv_transfer_state.transfer_length = pos;
  dtv_transfer_state.crc16 = crc16;

  return TRANSFER_OK;
}

u08 diagnose_dtv_recv_block(void)
{
  u08 result;
  u16 length = dtv_transfer_state.length;
  u08 pattern = PARAM_BYTE(PARAM_BYTE_DIAGNOSE_PATTERN);

  u16 pos = 0;
  u16 crc16 = dtv_transfer_state.crc16;
  while(length) {
    // transfer pattern byte to host
    result = current_host_transfer_funcs->transfer_byte(&pattern);
    if(result!=TRANSFER_OK)
      break;

    // update checksum
    crc16 = _crc16_update(crc16,pattern);

    pos++;
    length--;
  }
  dtv_transfer_state.transfer_length = pos;
  dtv_transfer_state.crc16 = crc16;

  return TRANSFER_OK;
}

// ----- diagnose host transfer funcs -----

u08 diagnose_host_mode = 0; // 0=read, 1=write, 2=verify

static u08 diagnose_begin_transfer(u32 length)
{ return TRANSFER_OK; }

static u08 diagnose_end_transfer(u08 lastStatus)
{ return lastStatus; }

static u08 diagnose_check_block(u16 crc16)
{ return TRANSFER_OK; }

static u08 diagnose_transfer_byte(u08 *data)
{
  u08 pattern = PARAM_BYTE(PARAM_BYTE_DIAGNOSE_PATTERN);

  if(diagnose_host_mode==DIAGNOSE_HOST_MODE_READ) {
    // read from host
    *data = pattern;
  }
  else {
    // write to host
    if(*data != pattern)
      return TRANSFER_ERROR_VERIFY_MISMATCH;
  }
  // do nothing in DIAGNOSE_HOST_MODE_WRITE
  return TRANSFER_OK;
}

host_transfer_funcs_t diagnose_host_transfer_funcs =
{
  .begin_transfer = diagnose_begin_transfer,
  .end_transfer   = diagnose_end_transfer,
  .check_block    = diagnose_check_block,
  .transfer_byte  = diagnose_transfer_byte
};

#endif // USE_DIAGNOSE


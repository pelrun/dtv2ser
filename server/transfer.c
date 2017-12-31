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

#include <stdint.h>
#include <util/crc16.h>

#include "board.h"

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

static uint8_t transfer_begin(uint8_t mode,uint32_t length)
{
  // reset transfer state
  transfer_state.length  = 0;
  transfer_state.ms_time = 0;
  transfer_state.result  = TRANSFER_OK;

  // begin host transfer
  uint8_t result = current_host_transfer_funcs->begin_transfer(length);
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

static uint8_t transfer_end(uint8_t result,uint32_t total_length,uint16_t ms_time)
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

uint8_t transfer_mem(uint8_t mode,uint32_t base,uint32_t length,uint16_t block_size)
{
  uint8_t result = transfer_begin(mode,length);
  if(result!=TRANSFER_OK)
    return result;

  // start timer
  uint32_t start = timer_now();

  // block copy loop
  uint32_t total_length = 0;
  uint8_t toggle = 1;
  while(length) {
    uint16_t offset = (uint16_t)(base & 0x3fff);
    uint16_t max_len = 0x4000 - offset;
    uint16_t block_len = min(length,block_size);
    uint16_t len = min(block_len,max_len);

    dtv_transfer_state.offset = offset;
    dtv_transfer_state.bank   = (uint8_t)(base >> 14);
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
    uint16_t transfer_length = dtv_transfer_state.transfer_length;
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
                      (timer_now() - start)/10);
}

uint8_t transfer_mem_block(uint8_t mode,uint8_t bank,uint16_t offset,uint16_t length)
{
  uint8_t result = transfer_begin(mode,length);
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

uint8_t diagnose_dtv_send_block(void)
{
  uint8_t result;
  uint16_t length = dtv_transfer_state.length;

  uint16_t pos = 0;
  uint16_t crc16 = dtv_transfer_state.crc16;
  while(length) {
    // transfer byte from host
    uint8_t data;
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

uint8_t diagnose_dtv_recv_block(void)
{
  uint8_t result;
  uint16_t length = dtv_transfer_state.length;
  uint8_t pattern = PARAM_BYTE(PARAM_BYTE_DIAGNOSE_PATTERN);

  uint16_t pos = 0;
  uint16_t crc16 = dtv_transfer_state.crc16;
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

uint8_t diagnose_host_mode = 0; // 0=read, 1=write, 2=verify

static uint8_t diagnose_begin_transfer(uint32_t length)
{ return TRANSFER_OK; }

static uint8_t diagnose_end_transfer(uint8_t lastStatus)
{ return lastStatus; }

static uint8_t diagnose_check_block(uint16_t crc16)
{ return TRANSFER_OK; }

static uint8_t diagnose_transfer_byte(uint8_t *data)
{
  uint8_t pattern = PARAM_BYTE(PARAM_BYTE_DIAGNOSE_PATTERN);

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


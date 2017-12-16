/*
 * dtvtrans.c - high level dtvtrans protocol
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

#include "dtvlow.h"
#include "dtvtrans.h"
#include "transfer.h"
#include "uart.h"
#include "uartutil.h"
#include "util.h"

// ----- internal tools -----

static uint8_t send_lohi(uint16_t word)
{
  uint8_t lo = (uint8_t)(word & 0xff);
  uint8_t hi = (uint8_t)(word >> 8);
  uint8_t status = dtvlow_send_byte(lo);
  if(status==TRANSFER_OK)
    status = dtvlow_send_byte(hi);
  return status;
}

// ----- send mem block -----

uint8_t dtvtrans_send_mem_block(void)
{
  uint8_t status;
  uint16_t len = dtv_transfer_state.length;

  dtvlow_state_send();

  // 1. send cmd write (uint8_t)
  status = dtvlow_send_byte(0x02);

  // 2. mode (uint8_t)
  if(status==TRANSFER_OK)
    status = dtvlow_send_byte(dtv_transfer_state.mode);

  // 3. bank (uint8_t)
  if(status==TRANSFER_OK)
    status = dtvlow_send_byte(dtv_transfer_state.bank);

  // 4. base (uint16_t)
  if(status==TRANSFER_OK)
    status = send_lohi(dtv_transfer_state.offset);

  // 5. len (uint16_t)
  if(status==TRANSFER_OK)
    status = send_lohi(len);

  // 6. block data
  uint8_t chk = 0;
  uint16_t i=0;
  uint16_t crc16 = dtv_transfer_state.crc16;
  uint8_t host_status = TRANSFER_OK;
  if(status==TRANSFER_OK) {
    while(i<len) {
      // get data from host if its still valid
      uint8_t data;
      if(host_status==TRANSFER_OK) {
        host_status = current_host_transfer_funcs->transfer_byte(&data);
      } else {
        // host transfer failed. now feed in zeros to finish dtvtrans
        data = 0;
      }

      // send byte
      status = dtvlow_send_byte(data);
      if(status!=TRANSFER_OK)
        break;

      // update checksum
      chk += data+1;
      crc16 = _crc16_update(crc16,data);
      i++;
    }
  }
  dtv_transfer_state.transfer_length = i;
  dtv_transfer_state.crc16 = crc16;

  // 7. check sum (uint8_t)
  if(status==TRANSFER_OK)
    status = dtvlow_send_byte(chk);

  dtvlow_state_recv();

  // 8. recv check
  uint8_t chk2 = 0;
  status = dtvlow_recv_byte(&chk2);

  dtvlow_state_off();

  if(host_status!=TRANSFER_OK)
    return host_status;
  if(status!=TRANSFER_OK)
    return status;
  else if(chk==chk2)
    return TRANSFER_OK;
  else
    return TRANSFER_ERROR_DTVTRANS_CHECKSUM;
}

// ----- receive mem block -----

uint8_t dtvtrans_recv_mem_block(void)
{
  uint8_t status;
  uint16_t len = dtv_transfer_state.length;

  dtvlow_state_send();

  // 1. send cmd read (uint8_t)
  status = dtvlow_send_byte(0x01);

  // 2. mode (uint8_t)
  if(status==TRANSFER_OK)
    status = dtvlow_send_byte(dtv_transfer_state.mode);

  // 3. bank (uint8_t)
  if(status==TRANSFER_OK)
    status = dtvlow_send_byte(dtv_transfer_state.bank);

  // 4. base (uint16_t)
  if(status==TRANSFER_OK)
    status = send_lohi(dtv_transfer_state.offset);

  // 5. len (uint16_t)
  if(status==TRANSFER_OK)
    status = send_lohi(len);

  dtvlow_state_recv();

  // 6. recv data
  uint8_t chk = 0;
  uint16_t i = 0;
  uint16_t crc16 = dtv_transfer_state.crc16;
  uint8_t host_status = TRANSFER_OK;
  if(status==TRANSFER_OK) {
    while(i<len) {
      // recv byte
      uint8_t data;
      status = dtvlow_recv_byte(&data);
      if(status!=TRANSFER_OK)
        break;

      // put data to host
      if(host_status==TRANSFER_OK) {
        host_status = current_host_transfer_funcs->transfer_byte(&data);
      }

      // update checksum
      chk += data+1;
      crc16 = _crc16_update(crc16,data);
      i++;
    }
  }
  dtv_transfer_state.transfer_length = i;
  dtv_transfer_state.crc16 = crc16;

  // 7. recv check sum (uint8_t)
  uint8_t chk2;
  if(status==TRANSFER_OK)
    status = dtvlow_recv_byte(&chk2);

  dtvlow_state_off();

  if(host_status!=TRANSFER_OK)
    return host_status;
  if(status!=TRANSFER_OK)
    return status;
  else if(chk==chk2)
    return TRANSFER_OK;
  else
    return TRANSFER_ERROR_DTVTRANS_CHECKSUM;
}

// ----- execute mem -----

#ifdef USE_OLDCMD

uint8_t dtvtrans_exec_mem(uint16_t addr)
{
  uint8_t status;

  dtvlow_state_send();

  // 1. send exec mem cmd (uint8_t)
  status = dtvlow_send_byte(0x03);
  if(status==TRANSFER_OK) {
    // 2. send addr (uint16_t)
    status = send_lohi(addr);
  }

  dtvlow_state_off();

  return status;
}

#endif

// ----- generic command -----

uint8_t dtvtrans_command(uint8_t command,uint8_t in_size,uint8_t *in_buf,uint8_t out_size)
{
  uint8_t i,data[2],j;

  dtvlow_state_send();

  // 1. first send command byte
  uint8_t status = dtvlow_send_byte(command);
  if(status==TRANSFER_OK) {

    // 2. send arguments
    if(in_size>0) {
      uart_start_reception();
      for(i=0;i<in_size;i++) {
        // send byte via dtvlow
        status = dtvlow_send_byte(in_buf[i]);
        if(status!=TRANSFER_OK)
          break;
      }
    }

    // 3. receive (optional) output bytes
    if((status==TRANSFER_OK)&&(out_size>0)) {

      // enter receive state
      dtvlow_state_recv();

      // variable size read: fetch size first
      uint8_t size = out_size;
      if(out_size==DTVTRANS_CMD_VARARG) {
        status = dtvlow_recv_byte(&size);

        // 3a. send size of output as hex byte
        if(status==TRANSFER_OK) {
          if(!uart_send_hex_byte_crlf(size))
            status = TRANSFER_ERROR_CLIENT_TIMEOUT;
        }
      }

      // 3b. fetch and send hex output bytes
      if(status==TRANSFER_OK) {
        for(i=0;i<size;i++) {

          // get byte from dtv
          status = dtvlow_recv_byte(&j);
          if(status!=TRANSFER_OK)
            break;

          // send byte to host
          byte_to_hex(j,data);
          if(!uart_send_data(data,2)) {
            status = TRANSFER_ERROR_CLIENT_TIMEOUT;
            break;
          }
        }
      }

      // terminate output bytes with a lf
      if(status==TRANSFER_OK) {
        if(!uart_send_crlf())
          status = TRANSFER_ERROR_CLIENT_TIMEOUT;
      }
    }
  }

  dtvlow_state_off();
  return status;
}


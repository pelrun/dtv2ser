/*
 * boot.c - implement boot protocol
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

#include "board.h"

#include "boot.h"

#include "dtvlow.h"
#include "uart.h"
#include "display.h"
#include "transfer.h"
#include "timer.h"

#ifdef USE_BOOT

static uint8_t send_hilo_boot(uint16_t word)
{
  uint8_t lo = (uint8_t)(word & 0xff);
  uint8_t hi = (uint8_t)(word >> 8);
  uint8_t status = dtvlow_send_byte_boot(hi);
  if(status==TRANSFER_OK)
    status = dtvlow_send_byte_boot(lo);
  return status;
}

static uint8_t dtvtrans_send_boot(uint16_t base,uint16_t length)
{
  uint8_t status;

  uart_start_reception();

  // send start byte
  uart_send(0);

  dtvlow_state_send();

  // 1. send start (uint16_t)
  status = send_hilo_boot(base);

  // 2. send end (uint16_t)
  uint16_t end = base + length - 1;
  if(status==TRANSFER_OK)
    status = send_hilo_boot(end);

  // 3. data
  uint8_t toggle = 1;
  uint8_t chk = 0;
  if(status==TRANSFER_OK) {
    while(length>0) {
      // get data from host if its still valid
      uint8_t data;
      if(!uart_read(&data)) {
        status = TRANSFER_ERROR_CLIENT_TIMEOUT;
        break;
      }

      // send byte
      status = dtvlow_send_byte_boot(data);
      if(status!=TRANSFER_OK)
        break;

      toggle ^= 1;
      if(toggle) {
        led_transmit_on();
      } else {
        led_transmit_off();
      }

      // update checksum
      chk += data+1;
      length--;
    }
  }

  // 4. check sum (uint8_t)
  if(status==TRANSFER_OK)
    status = dtvlow_send_byte_boot(chk);

  dtvlow_state_off();

  // send status (and chk if OK)
  uart_send(status);
  if(status==TRANSFER_OK)
    uart_send(chk);

  uart_stop_reception();

  led_transmit_off();

  return status;
}

void exec_boot_memory(void)
{
  uint16_t addr = CMDLINE_ARG_WORD(0);
  uint16_t len  = CMDLINE_ARG_WORD(1);

  timer_10ms = 0;

  uint8_t status = dtvtrans_send_boot(addr,len);

  // setup transfer state
  transfer_state.ms_time = timer_10ms;
  transfer_state.result  = status;

  if(status!=TRANSFER_OK)
    error_condition();
}

#endif


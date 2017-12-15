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

#include "boot.h"

#include "dtvlow.h"
#include "uart.h"
#include "display.h"
#include "transfer.h"
#include "timer.h"

#ifdef USE_BOOT

static u08 send_hilo_boot(u16 word)
{
  u08 lo = (u08)(word & 0xff);
  u08 hi = (u08)(word >> 8);
  u08 status = dtvlow_send_byte_boot(hi);
  if(status==TRANSFER_OK)
    status = dtvlow_send_byte_boot(lo);
  return status;
}

static u08 dtvtrans_send_boot(u16 base,u16 length)
{
  u08 status;

  uart_start_reception();

  // send start byte
  uart_send(0);

  dtvlow_state_send();

  // 1. send start (u16)
  status = send_hilo_boot(base);

  // 2. send end (u16)
  u16 end = base + length - 1;
  if(status==TRANSFER_OK)
    status = send_hilo_boot(end);

  // 3. data
  u08 toggle = 1;
  u08 chk = 0;
  if(status==TRANSFER_OK) {
    while(length>0) {
      // get data from host if its still valid
      u08 data;
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

  // 4. check sum (u08)
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
  u16 addr = CMDLINE_ARG_WORD(0);
  u16 len  = CMDLINE_ARG_WORD(1);

  timer_10ms = 0;

  u08 status = dtvtrans_send_boot(addr,len);

  // setup transfer state
  transfer_state.ms_time = timer_10ms;
  transfer_state.result  = status;

  if(status!=TRANSFER_OK)
    error_condition();
}

#endif


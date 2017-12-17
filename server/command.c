/*
 * command.c - handle commands
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

#include "command.h"

#include "display.h"
#include "uart.h"
#include "uartutil.h"
#include "timer.h"
#include "dtvtrans.h"
#include "dtvlow.h"
#include "param.h"
#include "cmdline.h"

// ----- Helpers -----

// enter error condition to timeout host transfer
void error_condition(void)
{
  uint8_t toggle = 1;
  led_error_on();

  uart_start_reception();

  // do some blinking
  uint8_t num = PARAM_BYTE(PARAM_BYTE_ERROR_CONDITION_LOOPS);
  for(uint8_t i=0;i<num;i++) {
    timer_delay_10ms(PARAM_WORD(PARAM_WORD_ERROR_CONDITION_DELAY));
    toggle ^= 1;
    if(toggle) {
      led_error_on();
    } else {
      led_error_off();
    }

    // drain read buffer
    while(uart_read_data_available()) {
      uint8_t dummy;
      uart_read(&dummy);
    }
  }

  uart_stop_reception();

  led_error_off();
}

// ---------- Commands ------------------------------------------------------

// ----- Go Memory -----

#ifdef USE_OLDCMD

void exec_go_memory(void)
{
  uint16_t addr = CMDLINE_ARG_WORD(0);

#ifdef USE_LCD
  lcd_clear();
  lcd_print_string(3,1,(uint8_t*)"goto");
  lcd_print_word(8,1,'a',addr);
#endif

  // perform go
  led_transmit_on();
  uint8_t status = dtvtrans_exec_mem(addr);
  led_transmit_off();

  uart_send_hex_byte_crlf(status);
}

#endif

// ----- Reset DTV -----

void exec_reset_dtv(void)
{
  uint8_t reset_mode = CMDLINE_ARG_BYTE(0);

#ifdef USE_LCD
  lcd_clear();
  lcd_print_string(0,1,(uint8_t*)"reset");
#endif

  // perform reset
  led_transmit_on();
  dtvlow_reset_dtv(reset_mode);
  led_transmit_off();

  // send result
  uart_send_hex_byte_crlf(0);
}

// ----- Version -----

void exec_version(void)
{
#ifdef USE_LCD
  lcd_clear();
  lcd_print_version();
#endif

  // return version number of dtv2ser
  uart_send_hex_word_crlf(VERSION_MAJ << 8 | VERSION_MIN);
}

// ----- Exec Generic Command -----

void exec_command(void)
{
  uint8_t cmd      = CMDLINE_ARG_BYTE(0);
  uint8_t out_size = CMDLINE_ARG_BYTE(1);
  // use var args here:
  uint8_t in_size  = CMDLINE_NUM_ARG_BYTE - 2;
  uint8_t *in_buf  = &CMDLINE_ARG_BYTE(2);

  uint8_t status   = dtvtrans_command(cmd,in_size,in_buf,out_size);
  uart_send_hex_byte_crlf(status);
}

// ----- Alive -----

void exec_is_alive(void)
{
  led_transmit_on();
  dtvlow_state_send();
  uint8_t status = dtvlow_is_alive(CMDLINE_ARG_WORD(0));
  dtvlow_state_off();
  led_transmit_off();
  uart_send_hex_byte_crlf(status);
}

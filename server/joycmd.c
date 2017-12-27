/*
 * joycmd.c - joystick commands
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

#include "joycmd.h"

#include "joy.h"
#include "display.h"
#include "timer.h"
#include "uart.h"

// ---------- Joystick ----------

#ifdef USE_JOYSTICK

// ----- joy stream -----

static uint8_t command;
static uint8_t value;
static uint16_t delay;

void exec_joy_stream(void)
{
  uart_start_reception();
  uart_send(0);

  joy_begin();

  uint8_t result = JOY_COMMAND_OK;
  uint8_t led_on = 0;
  while(1) {
    // wait for next command
    while(!uart_read(&command));

    // extract command and value
    value = command & JOY_MASK;
    command &= JOY_COMMAND_MASK;

    // exit stream command
    if(command==JOY_COMMAND_EXIT) {
      // reply status OK
      break;
    }
    // set value command
    else if(command==JOY_COMMAND_OUT) {
      joy_out(value);
      led_on ^= 1;
      if(led_on) {
        led_transmit_on();
      } else {
        led_transmit_off();
      }
    }
    // wait command
    else if(command==JOY_COMMAND_WAIT) {
      delay = value;
      timer_10ms = 0;
      while(timer_10ms<delay) {
      }
    }
    else {
      result = JOY_COMMAND_ERROR;
      break;
    }
  }

  joy_out(0);
  joy_end();

  uart_send(result);
  uart_stop_reception();

  led_transmit_off();

  if(result!=JOY_COMMAND_OK)
    error_condition();
}

#endif

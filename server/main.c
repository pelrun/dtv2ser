/*
 * main.c - main loop
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
#include "display.h"
#include "cmdline.h"
#include "uart.h"
#include "uartutil.h"
#include "timer.h"
#include "dtvlow.h"
#include "param.h"
#include "board.h"

int main (void){
  // board init. e.g. switch off watchdog
  board_init();

  // setup HW
  led_init();

  // setup timer
  timer_init();

#ifdef USE_LCD
  lcd_init();
#endif

#ifdef USE_BEEPER
  beeper_init();
#endif

  // setup serial
  uart_init();

  // dtvtrans interface init
  dtvlow_state_init();

#ifdef USE_BEEPER
  // welcome beep
  beeper_beep(1);
#endif
#ifdef USE_LCD
  // welcome message
  lcd_clear();
  lcd_print_version();
#endif

  // setup parameters
  param_init();

  // init cmdline
  cmdline_init();
  // main loop
  while(1) {
    cmdline_handle();
  }

  return 0;
}

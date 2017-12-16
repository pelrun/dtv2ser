/*
 * cmdline.c - command line input handling
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

#include "cmdline.h"
#include "cmdtable.h"
#include "uart.h"
#include "uartutil.h"
#include "display.h"
#include "util.h"
#include "timer.h"
#include "param.h"

// buffer for user input
static uint8_t cmdline_buf[CMDLINE_SIZE];
// current position in command line
static uint8_t cmdline_pos = 0;
// flag for command line error
static uint8_t cmdline_error = 0;

// local functions
static void handle_return(void);
static command_t *find_command(uint8_t *data);
static uint8_t parse_args(uint8_t *pattern,uint8_t *data,uint8_t len,cmdline_args_t *args);

// keep a set of arguments
cmdline_args_t cmdline_args;

// ----- cmdline_init -----
void cmdline_init(void)
{
  cmdline_pos = 0;

  // signal ready state
  led_ready_on();
  led_error_off();
  uart_start_reception();
}

static void cmdline_set_error(void)
{
  led_error_on();
  cmdline_error = 1;
  timer_10ms = 0;
}

// ----- cmdline_handle -----
// call regurlarly to see if user input is available
void cmdline_handle(void)
{
  // read chars
  while(uart_read_data_available()) {
    uint8_t data;
    uart_read(&data);

    // LF ends line
    if((data=='\n')||(data=='\r')) {
      if(cmdline_pos>0) {
        // block rx
        uart_stop_reception();
        led_ready_off();

        // handle command
        handle_return();

        // allow rx
        uart_start_reception();
        led_ready_on();
      }
    }
    // erase
    else if((data==8)||(data==0x7f)) {
      if(cmdline_pos>0)
        cmdline_pos--;
      else {
#ifdef USE_BEEPER
        beeper_beep(1);
#endif
        cmdline_set_error();
      }
    }
    // normal char
    else if(data>=' ') {
      if(cmdline_pos<CMDLINE_SIZE)
        cmdline_buf[cmdline_pos++] = data;
      else {
#ifdef USE_BEEPER
        // line too long
        beeper_beep(1);
#endif
        cmdline_set_error();
      }
    }
  }

  // disable error led?
  uint16_t timeout = PARAM_WORD(PARAM_WORD_ERROR_CONDITION_DELAY);
  if(cmdline_error && (timer_10ms > timeout)) {
    led_error_off();
    cmdline_error = 0;
  }

#ifdef SHOW_RTS
  // show a valid RTS signal with the transmit LED
  if(uart_get_rts())
    led_transmit_on();
  else
    led_transmit_off();
#endif
}

// ----- handle return -----
// buffer is filled and user pressed return
static void handle_return(void)
{
  uint8_t status = CMDLINE_STATUS_OK;
  command_t *cmd = 0;

  // line too long?
  if(cmdline_pos==CMDLINE_SIZE) {
    status = CMDLINE_ERROR_LINE_TOO_LONG;
  }
  // nothing entered
  else if(cmdline_pos==0) {
    return;
  }
  // something entered
  else {
    // terminate buffer
    cmdline_buf[cmdline_pos] = 0;

    // search command
    cmd = find_command(cmdline_buf);
    if(cmd!=0) {
      // parse arguments for command
      status = parse_args(cmd->args_pattern,
                          cmdline_buf+cmd->len,
                          cmdline_pos-cmd->len,
                          &cmdline_args);
    } else {
      // unknown command
      status = CMDLINE_ERROR_UNKNOWN_COMMAND;
    }
  }

  // return command line status to client
  uart_send_hex_byte_crlf(status);

  // execute command if all went well
  if((cmd!=0)&&(status==CMDLINE_STATUS_OK)) {
    led_error_off();
    cmd->execute_cmd();
  }
  // set error led
  else {
    cmdline_set_error();
  }

  // reset pos counter
  cmdline_pos = 0;
}

// ----- find_command -----
static command_t *find_command(uint8_t *data)
{
  command_t *cmd = command_table;
  while(cmd->len>0) {
    uint8_t i;
    for(i=0;i<cmd->len;i++) {
      if(cmd->name[i]!=data[i])
        break;
    }
    if(i==cmd->len)
      return cmd;
    cmd++;
  }
  return 0;
}

// ----- parse args -----
static uint8_t parse_args(uint8_t *pattern,
                      uint8_t *data,uint8_t len,
                      cmdline_args_t *args)
{
  args->num_byte  = 0;
  args->num_word  = 0;
  args->num_dword = 0;

  // skip spaces
  while(*data==' ') {
    data++; len--;
  }

  // no arguments allowed
  if(pattern==0) {
    if(len==0)
      return CMDLINE_STATUS_OK;
    else
      return CMDLINE_ERROR_NO_ARGS_ALLOWED;
  }

  // decode pattern and parse
  while(*pattern) {
    // pick next pattern
    uint8_t p = *pattern;
    if(p!='*')
      pattern++;

    // no more data in cmd line
    if(len==0) {
      if(p=='*') {
        // in var arg mode we simply finish
        break;
      } else {
        // found a pattern but no data -> error
        return CMDLINE_ERROR_TOO_FEW_ARGS;
      }
    }

    switch(p) {
    case 'b': // parse byte
    case '*': // var arg mode
      if(len<2)
        return CMDLINE_ERROR_ARG_TOO_SHORT;
      if(args->num_byte == CMDLINE_MAX_ARG_BYTE)
        return CMDLINE_ERROR_TOO_MANY_ARGS;
      if(parse_byte(data,&args->arg_byte[args->num_byte]))
        args->num_byte++;
      else
        return CMDLINE_ERROR_NO_HEX_ARG;
      len-=2;
      data+=2;
      break;
    case 'w': // parse word
      if(len<4)
        return CMDLINE_ERROR_ARG_TOO_SHORT;
      if(parse_word(data,&args->arg_word[args->num_word]))
        args->num_word++;
      else
        return CMDLINE_ERROR_NO_HEX_ARG;
      len-=4;
      data+=4;
      break;
    case 't': // parse tri byte
      if(len<6)
        return CMDLINE_ERROR_ARG_TOO_SHORT;
      if(parse_dword6(data,&args->arg_dword[args->num_dword]))
        args->num_dword++;
      else
        return CMDLINE_ERROR_NO_HEX_ARG;
      len-=6;
      data+=6;
      break;
    default:
      break;
    }

    // skip spaces
    while(*data==' ') {
      data++; len--;
    }
  }

  if(len==0)
    return CMDLINE_STATUS_OK;
  else
    return CMDLINE_ERROR_TOO_MANY_ARGS;
}


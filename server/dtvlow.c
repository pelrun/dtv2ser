/*
 * dtvlow.c - low level dtvtrans protocol
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

#include "hal.h"

#include "timer.h"
#include "dtvlow.h"
#include "transfer.h"
#include "param.h"

void dtvlow_state_clear(void)
{
  dtvlow_rst(1);

  dtvlow_data(0b111);
  dtvlow_clk(1);
  dtvlow_ack(1);
}

void dtvlow_reset_dtv(uint8_t mode)
{
  uint16_t pre_delay = PARAM_WORD(PARAM_WORD_DTVLOW_PREPARE_RESET_DELAY);
  uint16_t delay = PARAM_WORD(PARAM_WORD_DTVLOW_RESET_DELAY);

  // 1.) RST=0
  dtvlow_rst(0);

  // delay 10 ms
  timer_delay_100us(pre_delay);

  // 2.) ACK=0, D0=0 - magick knock sequence for dtvtrans
  //     ACK=0, D1=0 - bypass dtvmon
  if(mode) {
    dtvlow_data(mode);
    dtvlow_ack(0);
  }

  // delay 10ms
  timer_delay_100us(pre_delay);

  // 3.) RST=1
  dtvlow_rst(1);

  // delay 1sec
  timer_delay_10ms(delay);

  // 4.) ACK=1, Dx=1
  dtvlow_data(0b111);
  dtvlow_ack(1);
}

static uint8_t wait_ack(uint8_t wait_value)
{
  uint8_t status = 0;

  uint16_t timeout = PARAM_WORD(PARAM_WORD_DTVLOW_WAIT_FOR_ACK_DELAY);
  timer_100us = 0;
  while(timer_100us<timeout) {
    uint8_t value = dtvlow_ack_get();
    if(value==wait_value) {
      status = 1;
      break;
    }
  }
  return status;
}

uint8_t dtvlow_is_alive(uint16_t timeout)
{
  // delay in 100us between samples taken
  uint16_t idle    = PARAM_WORD(PARAM_WORD_IS_ALIVE_IDLE);

  // sample ack signal and determine value: repeat * delay * 100us
  uint8_t repeat  = PARAM_BYTE(PARAM_BYTE_IS_ALIVE_REPEAT);
  uint8_t delay   = PARAM_BYTE(PARAM_BYTE_IS_ALIVE_DELAY);

  // stages of clock steps
  uint8_t steps = 0;

  // first ack
  uint8_t ack;

  // until timeout occurs
  timer_10ms = 0;
  while(timer_10ms < timeout) {

    // trigger a clock pulse depending on state
    if((steps&1)==0) {
      // set clk=0
      dtvlow_clk(0);
      ack = 0;
    } else {
      // set clk=1
      dtvlow_clk(1);
      ack = 1;
    }

    // make sure the ack signal has and holds the value
    uint8_t i=0;
    while(i<repeat) {
      // check ACK level
      uint8_t value = dtvlow_ack_get();
      if(value!=ack)
        break;

      i++;
      if(i==repeat) {
        steps ++;
        if(steps==4)
          return TRANSFER_OK;
      } else {
        // wait a bit
        timer_delay_100us(delay);
      }
    }

    // wait a bit to check signal again
    timer_delay_100us(idle);
  }

  return TRANSFER_ERROR_NOT_ALIVE;
}

uint8_t dtvlow_send_byte(uint8_t byte)
{

#if 0
  // make sure ack is high
  if(!wait_ack(1))
    return TRANSFER_ERROR_DTVLOW_BEGIN;
#endif

  // bit 7-5
  dtvlow_data(byte>>5);
  dtvlow_clk(0);

  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK1;

  // bit 4-2
  // set dx and clk=1
  dtvlow_data(byte>>2);
  dtvlow_clk(1);

  if(!wait_ack(1))
    return TRANSFER_ERROR_DTVLOW_NOACK2;

  // bit 1-0
  // set dx and clk=0
  dtvlow_data(byte & 0x03);
  dtvlow_clk(0);

  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK3;

  // finally dx=1, clk=1
  dtvlow_data(0b111);
  dtvlow_clk(1);

  if(!wait_ack(1))
    return TRANSFER_ERROR_DTVLOW_NOACK4;

  return TRANSFER_OK;
}

#define DELAY_FOR_RECV dtvlow_recv_delay(delay);

uint8_t dtvlow_recv_byte(uint8_t *byte)
{
  uint8_t value;
  uint8_t delay = PARAM_BYTE(PARAM_BYTE_DTVLOW_RECV_DELAY);

  *byte = 0;

  // bit 7-5
  // clk=0
  dtvlow_clk(0);
  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK1;
  DELAY_FOR_RECV;
  value = dtvlow_data_get();
  *byte |= (value << 5);

  // bit 4-2
  // clk=1
  dtvlow_clk(1);
  if(!wait_ack(1))
    return TRANSFER_ERROR_DTVLOW_NOACK2;
  DELAY_FOR_RECV;
  value = dtvlow_data_get();
  *byte |= (value << 2);

  // bit 1-0
  // clk=0
  dtvlow_clk(0);
  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK3;
  DELAY_FOR_RECV;
  value = dtvlow_data_get();
  *byte |= (value & 0x3);

  // finally, clk=1
  dtvlow_clk(1);
  if(!wait_ack(1))
    return TRANSFER_ERROR_DTVLOW_NOACK4;

  return TRANSFER_OK;
}

#ifdef USE_BOOT

uint8_t dtvlow_send_byte_boot(uint8_t byte)
{
  // bit 7-6 clk=0
  dtvlow_data(byte>>6);
  dtvlow_clk(0);

  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK1;

  // bit 5-4 clk=1
  dtvlow_data((byte>>4) & 0x03);
  dtvlow_clk(1);

  if(!wait_ack(1))
    return TRANSFER_ERROR_DTVLOW_NOACK2;

  // bit 3-2 clk=0
  dtvlow_data((byte>>2) & 0x03);
  dtvlow_clk(0);

  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK3;

  // bit 1-0 clk=1
  dtvlow_data(byte & 0x03);
  dtvlow_clk(1);

  if(!wait_ack(1))
    return TRANSFER_ERROR_DTVLOW_NOACK4;

  return TRANSFER_OK;
}

#endif



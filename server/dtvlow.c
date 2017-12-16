/*
 * dtvlow.c - low level dtvtrans protocol
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

#include <avr/io.h>
#include <util/delay.h>

#include "timer.h"
#include "dtvlow.h"
#include "transfer.h"
#include "param.h"

void dtvlow_state_init(void)
{
  // set reset as high input
  DTVLOW_ACKRESET_DDR  &= ~DTVLOW_RESET_MASK;
  // reset is high
  DTVLOW_ACKRESET_PORT |=  DTVLOW_RESET_MASK;

  dtvlow_state_off();
}

void dtvlow_state_off(void)
{
  // Input:  Dx, CLK, ACK
  // Output: -

  // set dx + clk input
  DTVLOW_DATACLK_DDR   &= ~(DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);
  // enable pullup
  DTVLOW_DATACLK_PORT  |=   DTVLOW_DATA_MASK|DTVLOW_CLK_MASK;

  // set ack input
  DTVLOW_ACKRESET_DDR  &=  ~DTVLOW_ACK_MASK;
  // enable pullup
  DTVLOW_ACKRESET_PORT |=   DTVLOW_ACK_MASK;
}

void dtvlow_state_send(void)
{
  // Input:  ACK
  // Output: Dx=1, CLK=1

  // set dx + clk output
  DTVLOW_DATACLK_DDR   |=  (DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);
  // all high
  DTVLOW_DATACLK_PORT  |=  (DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);

  // set ack input
  DTVLOW_ACKRESET_DDR  &=  ~DTVLOW_ACK_MASK;
  // enable pullup
  DTVLOW_ACKRESET_PORT |=   DTVLOW_ACK_MASK;
}

void dtvlow_state_recv(void)
{
  // Input:  Dx, ACK, Reset
  // Output: CLK=1

  // set dx input, clk output
  DTVLOW_DATACLK_DDR   &=  ~DTVLOW_DATA_MASK;
  DTVLOW_DATACLK_DDR   |=   DTVLOW_CLK_MASK;
  // all high
  DTVLOW_DATACLK_PORT  |=  (DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);

  // set ack input
  DTVLOW_ACKRESET_DDR  &=  ~DTVLOW_ACK_MASK;
  // enable pullup
  DTVLOW_ACKRESET_PORT |=   DTVLOW_ACK_MASK;
}

void dtvlow_reset_dtv(uint8_t mode)
{
  uint16_t pre_delay = PARAM_WORD(PARAM_WORD_DTVLOW_PREPARE_RESET_DELAY);
  uint16_t delay = PARAM_WORD(PARAM_WORD_DTVLOW_RESET_DELAY);

  // output: ACK,Dx,RST
  DTVLOW_ACKRESET_DDR |= DTVLOW_ACK_MASK | DTVLOW_RESET_MASK;
  DTVLOW_DATACLK_DDR  |= DTVLOW_DATA_MASK;

  // 1.) RST=0
  DTVLOW_ACKRESET_PORT &= ~DTVLOW_RESET_MASK;

  // delay 10 ms
  timer_delay_100us(pre_delay);

  // 2.) ACK=0, D0=0 - magick knock sequence for dtvtrans
  //     ACK=0, D1=0 - bypass dtvmon
  if(mode) {
    DTVLOW_ACKRESET_PORT &= ~DTVLOW_ACK_MASK;
    DTVLOW_DATACLK_PORT  &= ~(mode << DTVLOW_DATA_SHIFT);
  }

  // delay 10ms
  timer_delay_100us(pre_delay);

  // 3.) RST=1
  DTVLOW_ACKRESET_PORT |= DTVLOW_RESET_MASK;

  // delay 1sec
  timer_delay_10ms(delay);

  // 4.) ACK=1, Dx=1
  DTVLOW_ACKRESET_PORT |= DTVLOW_ACK_MASK;
  DTVLOW_DATACLK_PORT  |= DTVLOW_DATA_MASK;

  // input: ACK,Dx,RST
  DTVLOW_ACKRESET_DDR  &=  ~(DTVLOW_ACK_MASK | DTVLOW_RESET_MASK);
  DTVLOW_DATACLK_DDR   &=  ~DTVLOW_DATA_MASK;
}

static uint8_t wait_ack(uint8_t wait_value)
{
  uint8_t status = 0;

  uint16_t timeout = PARAM_WORD(PARAM_WORD_DTVLOW_WAIT_FOR_ACK_DELAY);
  timer_100us = 0;
  while(timer_100us<timeout) {
    uint8_t value = DTVLOW_ACKRESET_PIN;
    if((value & DTVLOW_ACK_MASK)==wait_value) {
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
      DTVLOW_DATACLK_PORT &= ~(DTVLOW_CLK_MASK);
      ack = 0;
    } else {
      // set clk=1
      DTVLOW_DATACLK_PORT |= DTVLOW_CLK_MASK;
      ack = DTVLOW_ACK_MASK;
    }

    // make sure the ack signal has and holds the value
    uint8_t i=0;
    while(i<repeat) {
      // check ACK level
      uint8_t value = DTVLOW_ACKRESET_PIN;
      if((value & DTVLOW_ACK_MASK)!=ack)
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
  uint8_t dx,value;

#if 0
  // make sure ack is high
  if(!wait_ack(DTVLOW_ACK_MASK))
    return TRANSFER_ERROR_DTVLOW_BEGIN;
#endif

  // bit 7-5
  dx = (byte >> 5) & 0x07;
  // set dx and clk=0
  value = DTVLOW_DATACLK_PORT;
  value &= ~(DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);
  value |= (dx << DTVLOW_DATA_SHIFT);
  DTVLOW_DATACLK_PORT = value;

  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK1;

  // bit 4-2
  dx = (byte >> 2) & 0x07;
  // set dx and clk=1
  value = DTVLOW_DATACLK_PORT;
  value &= ~(DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);
  value |= (dx << DTVLOW_DATA_SHIFT) | DTVLOW_CLK_MASK;
  DTVLOW_DATACLK_PORT = value;

  if(!wait_ack(DTVLOW_ACK_MASK))
    return TRANSFER_ERROR_DTVLOW_NOACK2;

  // bit 1-0
  dx = byte & 0x03;
  // set dx and clk=0
  value = DTVLOW_DATACLK_PORT;
  value &= ~(DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);
  value |= (dx << DTVLOW_DATA_SHIFT);
  DTVLOW_DATACLK_PORT = value;

  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK3;

  // finally dx=1, clk=1
  value = DTVLOW_DATACLK_PORT;
  value |= (DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);
  DTVLOW_DATACLK_PORT = value;

  if(!wait_ack(DTVLOW_ACK_MASK))
    return TRANSFER_ERROR_DTVLOW_NOACK4;

  return TRANSFER_OK;
}

#define DELAY_FOR_RECV _delay_loop_1(delay);

uint8_t dtvlow_recv_byte(uint8_t *byte)
{
  uint8_t value;
  uint8_t delay = PARAM_BYTE(PARAM_BYTE_DTVLOW_RECV_DELAY);

  *byte = 0;

  // bit 7-5
  // clk=0
  DTVLOW_DATACLK_PORT &= ~DTVLOW_CLK_MASK;
  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK1;
  DELAY_FOR_RECV;
  value = (DTVLOW_DATACLK_PIN & DTVLOW_DATA_MASK) >> DTVLOW_DATA_SHIFT;
  *byte |= (value << 5);

  // bit 4-2
  // clk=1
  DTVLOW_DATACLK_PORT |= DTVLOW_CLK_MASK;
  if(!wait_ack(DTVLOW_ACK_MASK))
    return TRANSFER_ERROR_DTVLOW_NOACK2;
  DELAY_FOR_RECV;
  value = (DTVLOW_DATACLK_PIN & DTVLOW_DATA_MASK) >> DTVLOW_DATA_SHIFT;
  *byte |= (value << 2);

  // bit 1-0
  // clk=0
  DTVLOW_DATACLK_PORT &= ~DTVLOW_CLK_MASK;
  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK3;
  DELAY_FOR_RECV;
  value = (DTVLOW_DATACLK_PIN & DTVLOW_DATA_MASK) >> DTVLOW_DATA_SHIFT;
  *byte |= (value & 0x3);

  // finally, clk=1
  DTVLOW_DATACLK_PORT |= DTVLOW_CLK_MASK;
  if(!wait_ack(DTVLOW_ACK_MASK))
    return TRANSFER_ERROR_DTVLOW_NOACK4;

  return TRANSFER_OK;
}

#ifdef USE_BOOT

uint8_t dtvlow_send_byte_boot(uint8_t byte)
{
  uint8_t dx,value;

  // bit 7-6
  dx = (byte >> 6) & 0x03;
  // set dx and clk=0
  value = DTVLOW_DATACLK_PORT;
  value &= ~(DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);
  value |= (dx << DTVLOW_DATA_SHIFT);
  DTVLOW_DATACLK_PORT = value;

  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK1;

  // bit 5-4
  dx = (byte >> 4) & 0x03;
  // set dx and clk=1
  value = DTVLOW_DATACLK_PORT;
  value &= ~(DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);
  value |= (dx << DTVLOW_DATA_SHIFT) | DTVLOW_CLK_MASK;
  DTVLOW_DATACLK_PORT = value;

  if(!wait_ack(DTVLOW_ACK_MASK))
    return TRANSFER_ERROR_DTVLOW_NOACK2;

  // bit 3-2
  dx = (byte >> 2) & 0x03;
  // set dx and clk=0
  value = DTVLOW_DATACLK_PORT;
  value &= ~(DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);
  value |= (dx << DTVLOW_DATA_SHIFT);
  DTVLOW_DATACLK_PORT = value;

  if(!wait_ack(0))
    return TRANSFER_ERROR_DTVLOW_NOACK3;

  // bit 1-0
  dx = byte & 0x03;
  // set dx and clk=1
  value = DTVLOW_DATACLK_PORT;
  value &= ~(DTVLOW_DATA_MASK|DTVLOW_CLK_MASK);
  value |= (dx << DTVLOW_DATA_SHIFT) | DTVLOW_CLK_MASK;
  DTVLOW_DATACLK_PORT = value;

  if(!wait_ack(DTVLOW_ACK_MASK))
    return TRANSFER_ERROR_DTVLOW_NOACK4;

  return TRANSFER_OK;
}

#endif



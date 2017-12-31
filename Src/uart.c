/*
 * uart.c - serial hw routines
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

#include "usbd_cdc_if.h"

#include "board.h"

#include "uart.h"
#include "param.h"
#include "display.h"

#define CIRC_BUF_SIZE 256

typedef struct
{
  volatile uint16_t in;
  volatile uint16_t out;
  volatile uint8_t data[CIRC_BUF_SIZE];
} Circular_Buffer_t;

#define CIRCBUF_LEN(c) ((uint16_t)(c.in - c.out) & (CIRC_BUF_SIZE-1))

static Circular_Buffer_t rx_buf;

// ---------- init ----------------------------------------------------------

void uart_init(void) 
{
  rx_buf.in = rx_buf.out = 0;
}

// ---------- read ----------------------------------------------------------

uint8_t uart_read_data_available(void)
{
  return rx_buf.in != rx_buf.out;
}

void uart_stop_reception(void)
{
}

void uart_start_reception(void)
{
  rx_buf.in = rx_buf.out = 0;
}

uint8_t uart_unread(uint8_t *data, uint16_t len)
{
  if (CIRCBUF_LEN(rx_buf) < len) return 0;
  for (uint16_t i=0; i<len; i++)
  {
    rx_buf.data[rx_buf.in & (CIRC_BUF_SIZE-1)] = data[i];
    rx_buf.in++;
  }
  return 1;
}

uint8_t uart_read(uint8_t *data)
{
  uint16_t timeout = HAL_GetTick()+(PARAM_WORD(PARAM_WORD_SERIAL_READ_AVAIL_TIMEOUT)/10);
  while(rx_buf.in == rx_buf.out) {
    if (HAL_GetTick() > timeout) {
      return 0;
    }
    __WFI();
  }

  *data = rx_buf.data[rx_buf.out & (CIRC_BUF_SIZE-1)];
  rx_buf.out++;

  return 1;
}

// ---------- send ----------------------------------------------------------

uint8_t uart_send(uint8_t data)
{
  uint16_t timeout = HAL_GetTick()+(PARAM_WORD(PARAM_WORD_SERIAL_SEND_READY_TIMEOUT)/10);
  while(CDC_Transmit_FS(&data,1) != USBD_OK) {
    if (HAL_GetTick() > timeout) {
      return 0;
    }
    __WFI();
  }
  
  return 1;
}


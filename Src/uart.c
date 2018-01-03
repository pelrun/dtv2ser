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
#include "timer.h"

#define CIRCBUF_SIZE 256

typedef struct
{
  volatile uint16_t in;
  volatile uint16_t out;
  volatile uint8_t data[CIRCBUF_SIZE];
} Circular_Buffer_t;

#define CIRCBUF_LEN(c) ((uint16_t)(c.in - c.out) & (CIRCBUF_SIZE-1))

static inline uint16_t circbuf_len(Circular_Buffer_t *c)
{
  return (c->in - c->out) & (CIRCBUF_SIZE-1);
}

static inline uint16_t circbuf_free(Circular_Buffer_t *c)
{
  return CIRCBUF_SIZE - circbuf_len(c);
}

static inline void circbuf_write(Circular_Buffer_t *c, uint8_t data)
{
  c->data[c->in++ & (CIRCBUF_SIZE-1)] = data;
}

static inline uint8_t circbuf_read(Circular_Buffer_t *c)
{
  return c->data[c->out++ & (CIRCBUF_SIZE-1)];
}


static Circular_Buffer_t rx_buf;
static Circular_Buffer_t tx_buf;

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
//  rx_buf.in = rx_buf.out;
}

uint8_t uart_unread(uint8_t *data, uint16_t len)
{
  for (uint16_t i=0; i<len; i++)
  {
    circbuf_write(&rx_buf, data[i]);
  }

  return (circbuf_free(&rx_buf) > CDC_DATA_FS_MAX_PACKET_SIZE);
}

uint8_t uart_read(uint8_t *data)
{
  timeout_t t = TIMEOUT(PARAM_WORD(PARAM_WORD_SERIAL_READ_AVAIL_TIMEOUT));
  while(rx_buf.in == rx_buf.out) {
    if (timer_expired(&t)) {
      return 0;
    }
    __WFI();
  }

  *data = circbuf_read(&rx_buf);

  // allow more data in if there's room in the buffer
  if (circbuf_free(&rx_buf) >= CDC_DATA_FS_MAX_PACKET_SIZE*3)
  {
    CDC_Resume_RX();
  }

  return 1;
}

// ---------- send ----------------------------------------------------------
#if 0
void uart_flush(void)
{
  __disable_irq();
  if (tx_buf.in > 0)
  {
    if (CDC_Transmit_FS((uint8_t*)tx_buf.data,tx_buf.in) == USBD_OK)
    {
      tx_buf.in = tx_buf.out = 0;
    }
  }
  __enable_irq();
}

void HAL_SYSTICK_Callback()
{
  static uint16_t wait = 0;
  if ((wait++ & 0xFF) == 0)
  {
    uart_flush();
  }
}

uint8_t uart_send(uint8_t data)
{
  circbuf_write(&tx_buf, data);

  if (data == '\n' || tx_buf.in >= CDC_DATA_FS_MAX_PACKET_SIZE)
  {
    uart_flush();
  }

  return 1;
}

#else

uint8_t uart_send(uint8_t data)
{
  while (CDC_Transmit_FS(&data,1) != USBD_OK);

  return 1;
}

#endif

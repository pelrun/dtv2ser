/*
 * uart.c - serial hw routines
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

#include <avr/io.h>
#include <avr/interrupt.h>

#include "board.h"

#include "uart.h"
#include "timer.h"
#include "param.h"
#include "display.h"

#ifdef UBRR0H

// for atmeg644
#define UBRRH  UBRR0H
#define UBRRL  UBRR0L
#define UCSRA  UCSR0A
#define UCSRB  UCSR0B
#define UCSRC  UCSR0C
#define UDRE   UDRE0
#define UDR    UDR0

#define RXC    RXC0
#define TXC    TXC0
#define DOR    DOR0
#define PE     UPE0

#endif

// calc ubbr from baud rate
#define UART_UBRR   F_CPU/16/UART_BAUD-1

#define UART_RX_BUF_SIZE 16
#define UART_RX_SET_CTS_POS  2
#define UART_RX_CLR_CTS_POS  13
static volatile uint8_t uart_rx_buf[UART_RX_BUF_SIZE];
static volatile uint8_t uart_rx_start = 0;
static volatile uint8_t uart_rx_end = 0;
static volatile uint8_t uart_rx_size = 0;

// ---------- init ----------------------------------------------------------

void uart_init(void)
{
  uart_init_extra();
  uart_init_rts_cts();

  cli();

  // baud rate
  UBRRH = (uint8_t)((UART_UBRR)>>8);
  UBRRL = (uint8_t)((UART_UBRR)&0xff);

  UCSRB = 0x98; // 0x18  enable tranceiver and transmitter, RX interrupt
  UCSRC = 0x86; // 0x86 -> use UCSRC, 8 bit, 1 stop, no parity, asynch. mode

  sei();
}

// ---------- read ----------------------------------------------------------

// receiver interrupt
#ifdef USART_RXC_vect
ISR(USART_RXC_vect)
#else
ISR(USART_RX_vect)
#endif
{
  uint8_t data = UDR;
  uart_rx_buf[uart_rx_end] = data;

  uart_rx_end++;
  if(uart_rx_end == UART_RX_BUF_SIZE)
    uart_rx_end = 0;

  uart_rx_size++;
  if(uart_rx_size == UART_RX_CLR_CTS_POS) {
    uart_set_cts(0);
  }

//#define CHECK_UART_ERROR
#ifdef CHECK_UART_ERROR
  // overrun?
  if(uart_rx_end==uart_rx_start) {
    led_error_on();
  }

  // uart error?
  uint8_t status = UCSRA;
  if ((status & (_BV(FE)|_BV(DOR)|_BV(PE))) != 0) {
    led_error_on();
  }
#endif
}

uint8_t uart_read_data_available(void)
{
  return uart_rx_start != uart_rx_end;
}

void uart_stop_reception(void)
{
  uart_set_cts(0); // clear CTS
}

void uart_start_reception(void)
{
  // clear buffer
  cli();

  uart_rx_start = 0;
  uart_rx_end = 0;
  uart_rx_size = 0;

  sei();

  uart_set_cts(1); // set CTS
}

uint8_t uart_read(uint8_t *data)
{
  // read for buffe to be filled
  timer_100us = 0;
  uint16_t timeout = PARAM_WORD(PARAM_WORD_SERIAL_READ_AVAIL_TIMEOUT);
  while(uart_rx_start==uart_rx_end) {
    if (timer_100us > timeout) {
      return 0;
    }
  }

  // read buffer
  cli();

  *data = uart_rx_buf[uart_rx_start];

  uart_rx_start++;
  if(uart_rx_start == UART_RX_BUF_SIZE)
    uart_rx_start = 0;

  uart_rx_size--;
  uint8_t size = uart_rx_size;

  sei();

  // enable CTS again
  if(size == UART_RX_SET_CTS_POS) {
    led_ready_off();
    uart_set_cts(1);
  }

  return 1;
}

// ---------- send ----------------------------------------------------------

uint8_t uart_send(uint8_t data)
{
#ifndef IGNORE_RTS
  // wait for RTS with timeout
  timer_100us = 0;
  uint16_t rts_timeout = PARAM_WORD(PARAM_WORD_SERIAL_RTS_TIMEOUT);

#ifdef SHOW_WAIT_RTS
  led_ready_on();
#endif
  while(uart_get_rts()==0) {
    if(timer_100us > rts_timeout) {
#ifdef SHOW_WAIT_RTS
      led_ready_off();
#endif
      return 0;
    }
  }
#ifdef SHOW_WAIT_RTS
  led_ready_off();
#endif
#endif

  // wait for transmitter to become ready
  timer_100us = 0;
  uint16_t timeout = PARAM_WORD(PARAM_WORD_SERIAL_SEND_READY_TIMEOUT);
  while(!( UCSRA & (1<<UDRE))) {
    if (timer_100us > timeout) {
      return 0;
    }
  }

  // send byte
  UDR = data;

  return 1;
}


/*
 * timer.c - hw timer
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

#include "timer.h"

void timer_init(void)
{
  cli();

  // ----- TIMER1 (16bit) -----
  // 1ms counter

  // set to CTC on OCR1A with prescale 8
  TCCR1A = 0x00;
  TCCR1B = _BV(WGM12) | _BV(CS11); // CTC + prescale 8
#ifdef TCCR1C
  TCCR1C = 0x00;
#endif

  // t_tick = prescale / F_CPPU = 8 / F_CPU
  // how many ticks n until 1 ms is reached?
  //
  // t_tick * n = 1 ms
  //
  // -> n = 1 * F_CPU / ( prescaler * 1000 )
  // -> compare val m = n -1

#define TIMER1_COMPARE_VAL  ((1 * F_CPU) / (8 * 1000)) - 1
#ifdef OCR1A
  OCR1A = TIMER1_COMPARE_VAL;
#else
  OCR1 = TIMER1_COMPARE_VAL;
#endif

  // reset timer
  TCNT1 = 0;

#ifdef TIMSK1
  // generate interrupt for OCIE1A
  TIMSK1 = _BV(OCIE1A);
#else
  TIMSK |= _BV(OCIE1A);
#endif

  sei();
}

// timer counter
volatile uint16_t timer_1ms = 0;

// timer1 compare A handler
ISR(TIMER1_COMPA_vect)
{
  timer_1ms++;
}

void timer_delay_1ms(uint16_t timeout)
{ 
  uint16_t start = timer_now();
  while((uint16_t)(timer_now()-start)<timeout);
}

uint8_t timer_expired(timeout_t *t)
{
  return (uint16_t)(timer_now() - t->start) > t->timeout;
}

uint16_t timer_now(void)
{
  uint16_t now;
  // remember, 16-bit reads on AVR aren't atomic...
  cli();
  now = timer_1ms;
  sei();
  return now;
}

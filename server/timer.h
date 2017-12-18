/*
 * timer.h - hw timer
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

#ifndef TIMER_H
#define TIMER_H

// init timers
void timer_init(void);

// busy wait with 1ms timer
void timer_delay_1ms(uint16_t timeout);

typedef struct {
  uint16_t start;
  uint16_t timeout;
} timeout_t;

#define TIMEOUT(x) { timer_now(), x }

uint8_t timer_expired(timeout_t *t);

uint16_t timer_now(void);

#endif


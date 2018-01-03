/*
 * param.c - parameter handling
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
#include <util/crc16.h>

#include "board.h"

#include "param.h"

// default parameters
static parameters_t default_parameters = {
  // 8 bit parameters
  {
    2,        // 0: PARAM_BYTE_DTVLOW_RECV_DELAY
    5,        // 1: PARAM_BYTE_ERROR_CONDITION_LOOPS
    0,        // 2: PARAM_BYTE_DIAGNOSE_PATTERN
    3,        // 3: PARAM_BYTE_IS_ALIVE_REPEAT
    2,       // 4: PARAM_BYTE_IS_ALIVE_DELAY
  },
  // 16 bit parameters
  {
    400,    // 0: PARAM_WORD_DTVLOW_WAIT_FOR_ACK_DELAY
    1,      // 1: PARAM_WORD_DTVLOW_PREPARE_RESET_DELAY
    1,      // 2: PARAM_WORD_DTVLOW_RESET_DELAY
    500,       // 3: PARAM_WORD_ERROR_CONDITION_DELAY
    500,     // 4: PARAM_WORD_SERIAL_RTS_TIMEOUT
    500,     // 5: PARAM_WORD_SERIAL_READ_AVAIL_TIMEOUT
    500,     // 6: PARAM_WORD_SERIAL_SEND_READY_TIMEOUT
    0x400,    // 7: PARAM_WORD_DTV_TRANSFER_BLOCK_SIZE
    20,      // 8: PARAM_WORD_IS_ALIVE_IDLE
  }
};

// current parameters
parameters_t parameters;

// build check sum for parameter block
static uint16_t calc_crc16(parameters_t *p)
{
  uint16_t crc16 = 0xffff;
  uint8_t *data = (uint8_t *)p;
  for(uint16_t i=0;i<sizeof(parameters_t);i++) {
    crc16 = _crc16_update(crc16,*data);
    data++;
  }
  return crc16;
}

uint8_t param_save(void)
{
  return PARAM_EEPROM_NOT_READY;
}

uint8_t param_load(void)
{
  return PARAM_EEPROM_NOT_READY;
}

void param_reset(void)
{
  // restore default param
  parameters = default_parameters;
}

void param_init(void)
{
  if(param_load()!=PARAM_OK)
    param_reset();
}

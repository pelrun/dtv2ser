/*
 * param.h - parameter handling
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

#ifndef PARAM_H
#define PARAM_H

// --- 8 bit parameters ---

// 0: dtvlow: how long to wait before reading from DTV
//    resolution: ~3 cycles -> ~200ns
//    default:    2
#define PARAM_BYTE_DTVLOW_RECV_DELAY           0

// 1: error condition loops
//    resolution: count
//    default:    3
#define PARAM_BYTE_ERROR_CONDITION_LOOPS       1

// 2: diagnose pattern
//    default:    0
#define PARAM_BYTE_DIAGNOSE_PATTERN            2

// 3: is alive repeat
//    default:    3
#define PARAM_BYTE_IS_ALIVE_REPEAT             3

// 4: is alive delay
//    resolution: 100us
//    default:    20      = 2ms
#define PARAM_BYTE_IS_ALIVE_DELAY              4

// number of 8 bit parameters
#define PARAM_BYTE_MAX                         5

// --- 16 bit parameters ---

// 0: dtvlow: how long to wait for an ACK from the DTV?
//    resolution: 100us
//    default:    0xfff
#define PARAM_WORD_DTVLOW_WAIT_FOR_ACK_DELAY  0

// 1: dtvlow: reset prepare delay
//    resolution: 100us
//    default:    100
#define PARAM_WORD_DTVLOW_PREPARE_RESET_DELAY 1

// 2: dtvlow: reset delay
//    resolution: 10ms
//    default:    100
#define PARAM_WORD_DTVLOW_RESET_DELAY         2

// 3: error condition delay
//    resolution: 10ms
//    default:    50
#define PARAM_WORD_ERROR_CONDITION_DELAY      3

// 4: serial rts timeout
//    resolution: 100us
//    default:    5000    = 500ms
#define PARAM_WORD_SERIAL_RTS_TIMEOUT         4

// 5: serial read data available timeout
//    resolution: 100us
//    default:    5000    = 500ms
#define PARAM_WORD_SERIAL_READ_AVAIL_TIMEOUT  5

// 6: serial send buffer ready timeout
//    resolution: 100us
//    default:    5000    = 500ms
#define PARAM_WORD_SERIAL_SEND_READY_TIMEOUT  6

// 7: dtv transfer block size
//    resolution: bytes
//    default:    0x400
#define PARAM_WORD_DTV_TRANSFER_BLOCK_SIZE    7

// 8: is alive idle
//    resolution: 100us
//    default:    200     = 20ms
#define PARAM_WORD_IS_ALIVE_IDLE              8

// number of 16 bit parameters
#define PARAM_WORD_MAX                        9

// combine all parameters
typedef struct {
  uint8_t param_8[PARAM_BYTE_MAX];
  uint16_t param_16[PARAM_WORD_MAX];
} parameters_t;

// access parameters
extern parameters_t parameters;

#define PARAM_BYTE(x)  (parameters.param_8[x])
#define PARAM_WORD(x)  (parameters.param_16[x])

// param result
#define PARAM_OK                  0
#define PARAM_EEPROM_NOT_READY    1
#define PARAM_EEPROM_CRC_MISMATCH 2

// init parameters. try to load from eeprom or use default
void param_init(void);
// save param to eeprom (returns param result)
uint8_t param_save(void);
// load param from eeprom (returns param result)
uint8_t param_load(void);
// reset param
void param_reset(void);

#endif

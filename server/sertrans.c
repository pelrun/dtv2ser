/*
 * sertrans.c - serial transfer
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
#include "uart.h"
#include "sertrans.h"
#include "util.h"

// ----- read -----

static uint8_t serial_begin_read_transfer(uint32_t length)
{
  uart_start_reception();

  // write 0 byte to signal start of read transfer
  if(uart_send(TRANSFER_OK))
    return TRANSFER_OK;
  else
    return TRANSFER_ERROR_CLIENT_TIMEOUT;
}

static uint8_t serial_end_read_transfer(uint8_t lastStatus)
{
  // write status to signal state of transfer
  if(!uart_send(lastStatus))
    lastStatus = TRANSFER_ERROR_CLIENT_TIMEOUT;

  uart_stop_reception();

  return lastStatus;
}

static uint8_t serial_read_byte(uint8_t *data)
{
  // read data byte from serial
  if(uart_read(data))
    return TRANSFER_OK;
  else
    return TRANSFER_ERROR_CLIENT_TIMEOUT;
}

static uint8_t serial_check_read_block(uint16_t crc16)
{
  // read crc16 word from serial
  uint8_t data[2];
  if(!uart_read(&data[0]))
    return TRANSFER_ERROR_CLIENT_TIMEOUT;
  if(!uart_read(&data[1]))
    return TRANSFER_ERROR_CLIENT_TIMEOUT;

  // compare crc16
  uint16_t host_crc16 = (uint16_t)data[0]<<8 | data[1];
  if(host_crc16 == crc16)
    return TRANSFER_OK;
  else
    return TRANSFER_ERROR_CRC16_MISMATCH;
}

host_transfer_funcs_t serial_host_read_funcs =
{
  .begin_transfer = serial_begin_read_transfer,
  .end_transfer   = serial_end_read_transfer,
  .check_block    = serial_check_read_block,
  .transfer_byte  = serial_read_byte
};

// ----- write -----

static uint8_t serial_begin_write_transfer(uint32_t length)
{
  uart_start_reception();

  uint8_t data;
  // write 0 byte to signal start of read transfer
  if(uart_read(&data) && (data==TRANSFER_OK))
    return TRANSFER_OK;
  else
    return TRANSFER_ERROR_CLIENT_TIMEOUT;
}

static uint8_t serial_end_write_transfer(uint8_t lastStatus)
{
  uint8_t data;
  // write status to signal state of transfer
  if(!uart_read(&data))
    data = TRANSFER_ERROR_CLIENT_TIMEOUT;

  uart_stop_reception();

  return data;
}

static uint8_t serial_check_write_block(uint16_t crc16)
{
  // send uint16_t crc16
  uint8_t data = crc16 >> 8;
  if(!uart_send(data))
    return TRANSFER_ERROR_CLIENT_TIMEOUT;
  data = crc16 & 0xff;
  if(!uart_send(data))
    return TRANSFER_ERROR_CLIENT_TIMEOUT;

  // is an error byte available???
  if(uart_read_data_available()) {
    return TRANSFER_ERROR_CLIENT_ABORT;
  }

  return TRANSFER_OK;
}

static uint8_t serial_write_byte(uint8_t *data)
{
  if(uart_send(*data))
    return TRANSFER_OK;
  else
    return TRANSFER_ERROR_CLIENT_TIMEOUT;
}

host_transfer_funcs_t serial_host_write_funcs =
{
  .begin_transfer = serial_begin_write_transfer,
  .end_transfer   = serial_end_write_transfer,
  .check_block    = serial_check_write_block,
  .transfer_byte  = serial_write_byte
};


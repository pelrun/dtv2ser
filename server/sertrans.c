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

static u08 serial_begin_read_transfer(u32 length)
{
  uart_start_reception();

  // write 0 byte to signal start of read transfer
  if(uart_send(TRANSFER_OK))
    return TRANSFER_OK;
  else
    return TRANSFER_ERROR_CLIENT_TIMEOUT;
}

static u08 serial_end_read_transfer(u08 lastStatus)
{
  // write status to signal state of transfer
  if(!uart_send(lastStatus))
    lastStatus = TRANSFER_ERROR_CLIENT_TIMEOUT;

  uart_stop_reception();

  return lastStatus;
}

static u08 serial_read_byte(u08 *data)
{
  // read data byte from serial
  if(uart_read(data))
    return TRANSFER_OK;
  else
    return TRANSFER_ERROR_CLIENT_TIMEOUT;
}

static u08 serial_check_read_block(u16 crc16)
{
  // read crc16 word from serial
  u08 data[2];
  if(!uart_read(&data[0]))
    return TRANSFER_ERROR_CLIENT_TIMEOUT;
  if(!uart_read(&data[1]))
    return TRANSFER_ERROR_CLIENT_TIMEOUT;

  // compare crc16
  u16 host_crc16 = (u16)data[0]<<8 | data[1];
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

static u08 serial_begin_write_transfer(u32 length)
{
  uart_start_reception();

  u08 data;
  // write 0 byte to signal start of read transfer
  if(uart_read(&data) && (data==TRANSFER_OK))
    return TRANSFER_OK;
  else
    return TRANSFER_ERROR_CLIENT_TIMEOUT;
}

static u08 serial_end_write_transfer(u08 lastStatus)
{
  u08 data;
  // write status to signal state of transfer
  if(!uart_read(&data))
    data = TRANSFER_ERROR_CLIENT_TIMEOUT;

  uart_stop_reception();

  return data;
}

static u08 serial_check_write_block(u16 crc16)
{
  // send u16 crc16
  u08 data = crc16 >> 8;
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

static u08 serial_write_byte(u08 *data)
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


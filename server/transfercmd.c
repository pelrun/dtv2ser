/*
 * transfercmd.c - handle transfer commands
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

#include "command.h"
#include "display.h"
#include "dtvlow.h"
#include "dtvtrans.h"
#include "uart.h"
#include "uartutil.h"
#include "sertrans.h"
#include "param.h"
#include "timer.h"
#include "joycmd.h"
#include "transfercmd.h"

// transfer mode
static u08 transfer_mode = TRANSFER_MODE_NORMAL;

// ----- Helpers -----

static void generic_transfer(void)
{
  u08 mode = CMDLINE_ARG_BYTE(0);
  u32 addr = CMDLINE_ARG_DWORD(0);
  u32 len  = CMDLINE_ARG_DWORD(1);

#ifdef USE_LCD
  lcd_print_dword6(8,0,'l',len);
  lcd_print_dword6(8,1,'a',addr);
  lcd_print_byte(0,1,'m',mode);
#endif

  // perform transfer
  u16 block_size = PARAM_WORD(PARAM_WORD_DTV_TRANSFER_BLOCK_SIZE);
  u08 status = transfer_mem(mode,addr,len,block_size);

#ifdef USE_LCD
  lcd_print_byte(3,0,'s',status);
#endif

  if(status!=TRANSFER_OK) {
    error_condition();
  }
}

#ifdef USE_BLOCKCMD

static void generic_block_transfer(void)
{
  u08 mode   = CMDLINE_ARG_BYTE(0);
  u08 bank   = CMDLINE_ARG_BYTE(1);
  u16 offset = CMDLINE_ARG_WORD(0);
  u16 length = CMDLINE_ARG_WORD(1);

#ifdef USE_LCD
  lcd_print_word(10,0,'l',length);
  lcd_print_word(10,1,'o',offset);
  lcd_print_byte(0,1,'m',mode);
  lcd_print_byte(5,1,'b',bank);
#endif

  // perform transfer
  u08 status = transfer_mem_block(mode,bank,offset,length);

#ifdef USE_LCD
  lcd_print_byte(5,0,'s',status);
#endif

  if(status!=TRANSFER_OK) {
    error_condition();
  }
}

#endif

static void set_read_pointers(void)
{
  // setup pointer for serial host transfer
#ifdef USE_DIAGNOSE
  if(transfer_mode!=TRANSFER_MODE_DTV_ONLY) {
#endif
    current_host_transfer_funcs = &serial_host_write_funcs;
#ifdef USE_DIAGNOSE
  } else {
    current_host_transfer_funcs = &diagnose_host_transfer_funcs;
    diagnose_host_mode = DIAGNOSE_HOST_MODE_WRITE;
  }
#endif

  // setup pointer for dtv transfer
#ifdef USE_DIAGNOSE
  if(transfer_mode!=TRANSFER_MODE_SERIAL_ONLY) {
#endif
    current_dtv_transfer_block_func = dtvtrans_recv_mem_block;
#ifdef USE_DIAGNOSE
  } else {
    current_dtv_transfer_block_func = diagnose_dtv_recv_block;
  }
#endif
}

static void set_write_pointers(void)
{
  // setup pointer for serial host transfer
#ifdef USE_DIAGNOSE
  if(transfer_mode!=TRANSFER_MODE_DTV_ONLY) {
#endif
    current_host_transfer_funcs = &serial_host_read_funcs;
#ifdef USE_DIAGNOSE
  } else {
    current_host_transfer_funcs = &diagnose_host_transfer_funcs;
    diagnose_host_mode = DIAGNOSE_HOST_MODE_READ;
  }
#endif

  // setup pointer for dtv transfer
#ifdef USE_DIAGNOSE
  if(transfer_mode!=TRANSFER_MODE_SERIAL_ONLY) {
#endif
    current_dtv_transfer_block_func = dtvtrans_send_mem_block;
#ifdef USE_DIAGNOSE
  } else {
    current_dtv_transfer_block_func = diagnose_dtv_send_block;
  }
#endif
}

// ---------- Commands ------------------------------------------------------

// ----- Read/Write Memory -----

void exec_read_memory(void)
{
  set_read_pointers();
  generic_transfer();
}

void exec_write_memory(void)
{
  set_write_pointers();
  generic_transfer();
}

// ----- Read/Write Block Memory -----

#ifdef USE_BLOCKCMD

void exec_block_read_memory(void)
{
  set_read_pointers();
  generic_block_transfer();
}

void exec_block_write_memory(void)
{
  set_write_pointers();
  generic_block_transfer();
}

#endif

// ----- Transfer Mode -----

void exec_transfer_mode(void)
{
  transfer_mode = CMDLINE_ARG_BYTE(0);
}

// ----- Transfer State -----

void exec_transfer_result(void)
{
  // send result code
  uart_send_hex_byte_crlf(transfer_state.result);
  // send transfer time in 10ms
  uart_send_hex_word_crlf(transfer_state.ms_time);
}

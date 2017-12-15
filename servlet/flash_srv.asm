;
; flash_srv.asm - main flash servlet code
;
; Written by
;  Christian Vogelgsang <chris@vogelgsang.org>
;
; This file is part of dtv2ser.
; See README for copyright notice.
;
;  This program is free software; you can redistribute it and/or modify
;  it under the terms of the GNU General Public License as published by
;  the Free Software Foundation; either version 2 of the License, or
;  (at your option) any later version.
;
;  This program is distributed in the hope that it will be useful,
;  but WITHOUT ANY WARRANTY; without even the implied warranty of
;  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;  GNU General Public License for more details.
;
;  You should have received a copy of the GNU General Public License
;  along with this program; if not, write to the Free Software
;  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
;  02111-1307  USA.
;

  include "dtv.asm"
  include "zeropage.asm"
  include "seg_begin.asm"

  ; ----- jump table ----
  ; $1000 - ident flash
  echo "ident_flash",.
  jmp ident_flash
  ; $1003 - generate flash map
  echo "gen_map",.
  jmp gen_map
  ; $1006 - program flash
  echo "program flash",.
  jmp program_flash

  ; ----- identify flash ----------------------------------------------------
ident_flash:
  jsr identify_flash
  lda flash_type
  rts

  ; ----- generate flash map ------------------------------------------------
gen_map:
  jsr  map_flash

; setup output buffer
  lda #<output
  sta output_ptr
  lda #>output
  sta output_ptr+1

; setup fptr_zp=$000000, eptr_zp=$000400
  ldy  #$04
  sty  eptr_zp+1
  ldy  #$00
  sty  fptr_zp
  sty  fptr_zp+1
  sty  fptr_zp+2
  sty  eptr_zp
  sty  eptr_zp+2
  sty  rptr_zp
  sty  rptr_zp+1
  sty  rptr_zp+2
csp_lp1:
  ldx #SECTOR_FILLED
  jsr  check_empty
  sta $d020
  cmp  #$ff
  bne  csp_skp3
  ldx #SECTOR_EMPTY
csp_skp3:

; store in output
  lda output_ptr
  sta ptr_zp
  lda output_ptr+1
  sta ptr_zp+1
  ldy #0
  txa
  sta (ptr_zp),y

  clc
  inc ptr_zp
  bne csp_1
  inc ptr_zp+1
csp_1:
  lda ptr_zp
  sta output_ptr
  lda ptr_zp+1
  sta output_ptr+1
; ----

  inc  rptr_zp
  bne  csp_skp1
  inc  rptr_zp+1
csp_skp1:

  lda  eptr_zp+1
  sta  fptr_zp+1
  lda  eptr_zp+2
  sta  fptr_zp+2

  lda  eptr_zp+1
  clc
  adc  #$04
  sta  eptr_zp+1
  bcc  csp_skp2
  inc  eptr_zp+2
csp_skp2:

  lda  fptr_zp+2  ; fptr_zp=$200000?
  cmp  #$20
  bne  csp_lp1    ; no, continue.

  jsr  unmap_flash
  rts

SECTOR_FILLED  equ  '*
SECTOR_EMPTY  equ  '.

  ; ----- flash operation ---------------------------------------------------
  ; input:
  ; $2000: <start lsb>,<start csb>,<start msb>
  ; $2003: <end lsb>,<end csb>,<end lsb>
  ;   acc: mode 0=erase 1=program 2=verify 3=check_empty
  ;
  ; output:
  ;   acc: error (0=ok)
  ;     x: check_empty_result ($ff=empty)
BUFFER_START equ $020000

program_flash:
  ; store erase or program mode!
  sta program_mode

  ; init check_empty_result
  lda #0
  sta check_empty_result

  ; reset error flag
  jsr err_ok

  ; identify flash
  jsr identify_flash
  lda err_num
  beq pf_flash_ok
  bra pfend2

pf_flash_ok:
  ; copy program start and end ptr to ftpr/eptr
  ldx	#2

pf2:
  lda program_start_ptr,x
  sta fptr_zp,x
  lda program_end_ptr,x
  sta eptr_zp,x
  dex
  bpl pf2

  ; set read pointer: BUFFER_START = 0x020000 RAM
  lda #0
  sta rptr_zp
  sta rptr_zp+1
  lda #(BUFFER_START>>16) & $ff
  sta rptr_zp+2

  ; mirror rom
  jsr mirror_roms

  ; map in flash
  jsr map_flash

  ; --- do it: erase or program ---
  lda program_mode
  sta $d020

  cmp #2 ; 2<- verify
  beq pf_verify
  cmp #3 ; 3<- compare
  beq pf_check_empty

  ; do program/erase
  jsr common_range
  bra pfend

pf_verify:
  ; --- verify ---
  jsr verify_range
  bra pfend

pf_check_empty:
  ; --- check empty ---
  jsr check_empty
  sta check_empty_result

  ; --- end of operations ---
pfend:
  ; unmap flash
  jsr unmap_flash

pfend2:
  ; unmirror rom
  jsr unmirror_roms

  ; return err_num in ACC
  lda err_num
  sta $d020

  ; return check empty result in X
  ldx check_empty_result
  rts

  ; ----- TLR's flash routines ----------------------------------------------
DEBUG_OUT  equ  0
  include "flash_io.asm"

  ; ----- data -----
  seg.u bss
output_ptr:
  ds.w 1
check_empty_result:
  ds.b 1

  include "seg_end.asm"

  ; ----- input/output buffer -----------------------------------------------
  seg.u my_data
  org $2000
output:
  ds.b 2048

  ; flash pointers
program_start_ptr = output
program_end_ptr = output + 3
  echo "program_start_ptr",program_start_ptr
  echo "program_end_ptr",program_end_ptr


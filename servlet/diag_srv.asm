;
; flash_srv.asm - diagnose servlet code
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

  processor 6502

  org   $1000

  ; diagnose
  ;
  ; in:  ACC=loops

diagnose:
  sta rnd

  ; init
  lda #0
  sta $d020
  sta $d021

  ; wait for rnd frames
  ldx rnd
d1:
  jsr wait_wb
  stx $d020
  dex
  bne d1

  ; exit
  lda #6
  sta $d020
  sta $d021

  lda #42
  ldx rnd
  ldy #0
  rts

wait_wb:
ww1:
  lda	$d011
  bpl	ww1
ww2:
  lda	$d011
  bmi	ww2
  rts

rnd:
  ds.b 1


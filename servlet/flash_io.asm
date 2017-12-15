;**************************************************************************
;*
;* FILE  flash_io.asm
;* Copyright (c) 2005, 2006, 2007 Daniel Kahlin <daniel@kahlin.net>
;* Written by Daniel Kahlin <daniel@kahlin.net>
;* $Id: flash_io.asm,v 1.80 2007-06-07 17:45:18 tlr Exp $
;*
;* DESCRIPTION
;*   Utility functions for program and verify flash memory.
;*
;* LAYOUT
;*   +---------------------------------+
;*   | Seg #0, Normal                  |
;*   | $0000                           |
;*   +---------------------------------+
;*   | Seg #1, RAM Read/Write Window   |
;*   | $4000                           |
;*   +---------------------------------+
;*   | Seg #2, Flash Read/Write Window |
;*   | $8000   (Possiby ROM)           |
;*   +---------------------------------+
;*   | Seg #3, Normal                  |
;*   | $c000                           |
;*   +---------------------------------+
;*
;******

;***
; configuration options
SUPPORT_PROGRAM_VERIFY	equ	1

; debug options
EXTRA_DEBUG		equ	0
COLOR_DEBUG		equ	0
ATMEL_TRACE_DEBUG	equ	0
ATMEL_TIMEOUT_DEBUG	equ	0

;***
; memory layout
MAX_FLASH_PAGE	equ	$20	; $000000-$200000
MIN_RAM_PAGE	equ	$02	; $020000-
MAX_RAM_PAGE	equ	$1d	; -$1d0000

TMP_START	equ	$1d0000	; $1d0000-$1e0000

MIRROR_PAGE	equ	$1e	; $1ea000-$1ec000/$1ee000-$1f0000
CHARSET_PAGE	equ	$38	; $003800-$004000

FLASH_WINDOW	equ	$4000
RAM_WINDOW	equ	$8000

;***
; internal constants

; byte/word programming times
;   Atmel AT47BV161T: typ=20 us, max=200 us
;   Atmel AT49BV161T: typ=20 us, max=200 us
;   Atmel AT49BV163A: typ=12 us, max=200 us
;   SST SST39VF1681:  typ=7 us,  max=10 us
ATMEL_PROG_BYTE_TIMEOUT	equ	200
SST_PROG_BYTE_TIMEOUT	equ	10

; sector erase times
;   Atmel AT47BV161T: typ=300 ms, max=400 ms
;   Atmel AT49BV161T: typ=300 ms, max=400 ms
;   Atmel AT49BV163A: typ=1.0 s,  max=5.0 s  (0.3/3.0 for 8 Kb sectors)
;   SST SST39VF1681:  typ=18 ms,  max=25 ms
ATMEL_SECTOR_ERASE_TIMEOUT	equ	5000000
SST_SECTOR_ERASE_TIMEOUT	equ	25000

; Atmel AT47BV161T hack for getting odd bytes running. >400 us
ATMEL_ODD_BYTE_HACK_TIMEOUT	equ	400


; Atmel $555*2 (A-1 is don't care)
; SST   $aaa
; i.e $aaa should work on both.
FLASH_OFFS_555	equ	$aaa

; Atmel $aaa*2 or $2aa*2 (A-1 is don't care)
; SST   $555
; i.e $555 should work on both.
FLASH_OFFS_AAA	equ	$555


; debugging macros
	mac	CDEBUG
	if	COLOR_DEBUG
	lda	#{1}
	sta	$d020
	endif	;COLOR_DEBUG
	endm

	seg	code
;**************************************************************************
;*
;* SECTION  jump table
;*
;* DESCRIPTION
;*
;******



;**************************************************************************
;*
;* NAME  check_wp
;*
;* DESCRIPTION
;*   check for soft write protect by checking fptr_zp+2
;*   NOTE: Size is hard coded compile time (normally $200000).
;*
;*   Ret:  C=0, writing allowed.
;*         C=1, writing forbidden.
;*
;******
check_wp_range:
	pha
	jsr	check_frange
	bcs	cwp_fl1
	pla
check_wp:
	pha
	lda	lowmem_wp
	beq	cwp_skp1
	lda	fptr_zp+2	; =$00xxxx
	beq	cwp_fl1		; yes, fail
cwp_skp1:
	jsr	check_faddr	; >=$200000
	bcs	cwp_fl1		; yes, fail
	pla
	clc
	rts
cwp_fl1:
	pla
	sec
	rts

; low-mem soft wp
lowmem_wp:
	dc.b	1


;**************************************************************************
;*
;* NAME  check_faddr, check_raddr, check_frange, check_rrange
;*
;* DESCRIPTION
;*   Address/range checking
;*   NOTE: Size is hard coded compile time (normally $200000).
;*
;*   Ret:  C=0, valid.
;*         C=1, invalid.
;*
;******
check_faddr:
	lda	fptr_zp+2
	cmp	#MAX_FLASH_PAGE	; C=1 if >=$200000
	rts

check_fend:
	lda	eptr_zp
	cmp	#$01
	lda	eptr_zp+1
	sbc	#$00
	lda	eptr_zp+2
	sbc	#MAX_FLASH_PAGE	; C=1 if >=$200001 (i.e > $200000)
	rts

check_frange:
	jsr	check_faddr
	bcs	cfr_ex1
	jsr	check_fend
	bcs	cfr_ex1
	jsr	sbc_fptr_eptr
;	bcs	cfr_ex1		; C=1 if fptr_zp >= eptr_zp
cfr_ex1:
	rts


	if	0
check_raddr:
	lda	rptr_zp+2
	cmp	#MAX_RAM_PAGE	; C=1 if >=$200000
	rts

check_rend:
	lda	eptr_zp
	cmp	#$01
	lda	eptr_zp+1
	sbc	#$00
	lda	eptr_zp+2
	sbc	#MAX_RAM_PAGE	; C=1 if >=$1d0001 (i.e > $1d0000)
	rts


check_rrange:
	jsr	check_raddr
	bcs	crr_ex1
	jsr	check_rend
	bcs	crr_ex1
	lda	rptr_zp
	cmp	eptr_zp
	lda	rptr_zp+1
	sbc	eptr_zp+1
	lda	rptr_zp+2
	sbc	eptr_zp+2
;	bcs	crr_ex1		; C=1 if rptr_zp >= eptr_zp
crr_ex1:
	rts
	endif

;**************************************************************************
;*
;* NAME  err_ok, err_wp, err_vfy, err_prog, err_imp, err_lock, err_range
;*
;* DESCRIPTION
;*
;******
ERR_OK		equ	0
ERR_WP		equ	1
ERR_VFY		equ	2
ERR_PROG	equ	3
ERR_IMP		equ	4
ERR_ERASE	equ	5
ERR_LOCK	equ	6
ERR_RANGE	equ	7
ERR_AUTO	equ	8

err_ok:
	lda	#ERR_OK
	sta	err_num
	clc
	rts
err_wp:
	lda	#ERR_WP
	dc.b	$2c
err_vfy:
	lda	#ERR_VFY
	dc.b	$2c
err_prog:
	lda	#ERR_PROG
	dc.b	$2c
err_imp:
	lda	#ERR_IMP
	dc.b	$2c
err_erase:
	lda	#ERR_ERASE
	dc.b	$2c
err_lock:
	lda	#ERR_LOCK
	dc.b	$2c
err_range:
	lda	#ERR_RANGE
	dc.b	$2c
err_auto:
	lda	#ERR_AUTO
	sta	err_num
	ldx	#2
err_lp1:
	lda	fptr_zp,x
	sta	err_addr,x
	dex
	bpl	err_lp1

	sec
	rts

err_num:
	dc.b	ERR_OK
err_addr:
	dc.b	0,0,0
err_actual:
	dc.b	0
err_expected:
	dc.b	0

  IF DEBUG_OUT
print_err:
	lda	err_num
	asl
	tax
	lda	err_tab,x
	ldy	err_tab+1,x
	jsr	print

	ldx	err_num
	lda	err_tab2,x
	and	#%01
	beq	per_ex1

	jsr	print_space
	lda	#"$"
	jsr	$ffd2
	lda	err_addr+2
	jsr	print_hex
	lda	err_addr+1
	jsr	print_hex
	lda	err_addr+0
	jsr	print_hex

	ldx	err_num
	lda	err_tab2,x
	and	#%10
	beq	per_ex1

	lda	#"="
	jsr	$ffd2
	lda	#"$"
	jsr	$ffd2
	lda	err_actual
	jsr	print_hex
	jsr	print_space
	lda	#"("
	jsr	$ffd2
	lda	#"$"
	jsr	$ffd2
	lda	err_expected
	jsr	print_hex
	lda	#")"
	jsr	$ffd2
per_ex1:
	jmp	print_cr

err_tab:
	dc.w	err_ok_msg
	dc.w	err_wp_msg
	dc.w	err_vfy_msg
	dc.w	err_prog_msg
	dc.w	err_imp_msg
	dc.w	err_erase_msg
	dc.w	err_lock_msg
	dc.w	err_range_msg
	dc.w	err_auto_msg
err_tab2:
	dc.b	%00
	dc.b	%00
	dc.b	%11
	dc.b	%11
	dc.b	%11
	dc.b	%01
	dc.b	%01
	dc.b	%01
	dc.b	%00

err_ok_msg:
	dc.b	"OK.",0
err_wp_msg:
	dc.b	"WRITE PROT!",0
err_vfy_msg:
	dc.b	"VERIFY ERROR!",0
err_prog_msg:
	dc.b	"PROG ERROR!",0
err_imp_msg:
	dc.b	"IMPOSSIBLE!",0
err_erase_msg:
	dc.b	"ERASE ERROR!",0
err_lock_msg:
	dc.b	"LOCKDOWN!",0
err_range_msg:
	dc.b	"OUT OF RANGE!",0
err_auto_msg:
	dc.b	"AUTOFLASH PARAM ERROR!",0

  ENDIF

;**************************************************************************
;*
;* NAME  program_range
;*
;* DESCRIPTION
;*   start: fptr_zp, fptr_zp+1, fptr_zp+2
;*          (rptr_zp, rptr_zp+1, rptr_zp+2)
;*   end+1: eptr_zp, eptr_zp+1, eptr_zp+2
;*   out: C=0 means ok, (C=1 means error)
;*
;******
program_mode:
	ds.b	1
program_range:
	lda	#1
	bra	common_range
;**************************************************************************
;*
;* NAME  erase_range
;*
;* DESCRIPTION
;*   start: fptr_zp, fptr_zp+1, fptr_zp+2
;*   end+1: eptr_zp, eptr_zp+1, eptr_zp+2
;*   out: C=0 means ok, (C=1 means error)
;*
;******
erase_range:
	lda	#0
common_range:
	sta	program_mode
	jsr	check_frange
	bcs	er_fl2
	jsr	check_wp
	bcs	er_fl3

	jsr	calculate_ranges
	bcc	er_skp6
er_fl2:
	jmp	err_range	; out of range, fail.
er_fl3:
	jmp	err_wp		; write protected, fail.

er_skp6:
; probably should check sector lockdowns here.

; traverse sectors, checking each one if empty
er_lp2:
	jsr	setup_sector_range
	bcc	er_skp1		; full sector

; first check if empty
	jsr	check_empty
	cmp	#$ff		; empty?
	beq	er_skp2		; yes, all done.

; this sector is partially covered
; we must dump and modify it.
	jsr	set_tmp_rptr
; dump the sector into the temporary buffer, erase and program back
	lda	this_sector
	jsr	sector_dump
	lda	this_sector
	jsr	sector_erase
	bcs	er_fl1		; erasing failed, exit!

	jsr	get_inv_range1
	bcs	er_skp3		; skip if empty range.
	if	EXTRA_DEBUG
	lda	#"A"
	jsr	print_range
	endif
; here we should probably check if this is already empty
	jsr	set_tmp_rptr_range
	jsr	program_range_int
	bcs	er_fl1		; programming failed, exit!
er_skp3:
	jsr	get_inv_range2	; skip if empty range.
	bcs	er_skp4
	if	EXTRA_DEBUG
	lda	#"B"
	jsr	print_range
	endif
; here we should probably check if this is already empty
	jsr	set_tmp_rptr_range
	jsr	program_range_int
	bcs	er_fl1		; programming failed, exit!
er_skp4:
	bra	er_skp2

er_skp1:
; full sector
; first check if empty
	jsr	check_empty
	cmp	#$ff		; empty?
	beq	er_skp2		; yes, all done.

; not empty, erase it!
	lda	this_sector
	jsr	sector_erase
	bcs	er_fl1		; erasing failed, exit!

er_skp2:
; if program range mode, programming occurs here
	lda	program_mode
	beq	er_skp5

	jsr	get_range

	ldx	#2
er_lp4:
	lda	buf_ptr,x
	sta	rptr_zp,x
	dex
	bpl	er_lp4
	jsr	program_range_int
	php
	ldx	#2
er_lp5:
	lda	rptr_zp,x
	sta	buf_ptr,x
	dex
	bpl	er_lp5
	plp
	bcs	er_fl1

er_skp5:

; check if it is the last sector
	lda	this_sector
	cmp	last_sector
	beq	er_ex1
	inc	this_sector
	bra	er_lp2
er_ex1:
; done!
	jmp	err_ok

er_fl1:
	sec
	rts

	if	EXTRA_DEBUG
print_range:
	jsr	$ffd2
	jsr	print_space
	jsr	print_fptr
	jsr	print_space
	jsr	print_eptr
	jsr	print_cr
	rts
	endif

;**************************************************************************
;*
;* NAME  calculate_ranges
;*
;* DESCRIPTION
;*   start: fptr_zp, fptr_zp+1, fptr_zp+2
;*   end+1: eptr_zp, eptr_zp+1, eptr_zp+2
;*   out: C=0 means ok, (C=1 means out of range!)
;*
;******
calculate_ranges:
	ldx	#2
car_lp1:
	lda	fptr_zp,x
	sta	start_ptr,x
	lda	eptr_zp,x
	sta	end_ptr,x
	lda	rptr_zp,x
	sta	buf_ptr,x
	dex
	bpl	car_lp1

; first determine the first and last sector to process.
	jsr	find_sector_num
	bcs	car_fl1		;out of range
	sta	first_sector
	lda	eptr_zp
	sec
	sbc	#1
	sta	fptr_zp
	lda	eptr_zp+1
	sbc	#0
	sta	fptr_zp+1
	lda	eptr_zp+2
	sbc	#0
	sta	fptr_zp+2
	jsr	find_sector_num
	bcs	car_fl1		;out of range
	sta	last_sector

	lda	first_sector
	sta	this_sector
	clc
car_fl1:
	rts

;**************************************************************************
;*
;* NAME  setup_sector_range
;*
;* DESCRIPTION
;*   calculate range within the current sector
;*   C=0 means that the whole sector is included.
;*   C=1 means that this sector is partially covered.
;*
;******
setup_sector_range:
	lda	this_sector
	jsr	set_sector_addr_end

; init flag
	ldy	#0

	ldx	#2
ssr_lp1:
	lda	fptr_zp,x
	sta	local_start,x
	sta	sector_start,x
	lda	eptr_zp,x
	sta	local_end,x
	sta	sector_end,x
	dex
	bpl	ssr_lp1

; check the start pointer  (local_start-start_ptr)
	lda	local_start
	cmp	start_ptr
	lda	local_start+1
	sbc	start_ptr+1
	lda	local_start+2
	sbc	start_ptr+2
;	bcc	ssr_skp1	;neg, start_ptr < local_start
	bcs	ssr_skp2

ssr_skp1:
; local_start < start_ptr
	ldx	#2
ssr_lp2:
	lda	start_ptr,x
	sta	local_start,x
	dex
	bpl	ssr_lp2
; flag that a pointer was modified
	iny

ssr_skp2:

; check the end pointer  (end_ptr-local_end)
	lda	end_ptr
	cmp	local_end
	lda	end_ptr+1
	sbc	local_end+1
	lda	end_ptr+2
	sbc	local_end+2
;	bcc	ssr_skp3	;neg, end_ptr > local_end
	bcs	ssr_skp4

ssr_skp3:
; end_ptr < local_end
	ldx	#2
ssr_lp3:
	lda	end_ptr,x
	sta	local_end,x
	dex
	bpl	ssr_lp3
; flag that a pointer was modified
	iny

ssr_skp4:
	jsr	get_range

	cpy	#0
	if	EXTRA_DEBUG
	php
	lda	#"R"
	jsr	print_range
	plp
	endif
	bne	ssr_ex1
	clc
	rts
ssr_ex1:
	sec
	rts

local_start:
	ds.b	3
local_end:
	ds.b	3
sector_start:
	ds.b	3
sector_end:
	ds.b	3

;**************************************************************************
;*
;* NAME  get_range, get_inv_range1, get_inv_range2
;*
;* DESCRIPTION
;*   C=0 means that the the range is >0
;*   C=1 means that the range is 0
;*
;******
get_range:
	ldx	#2
ger_lp1:
	lda	local_start,x
	sta	fptr_zp,x
	lda	local_end,x
	sta	eptr_zp,x
	dex
	bpl	ger_lp1
	rts
get_inv_range1:
	ldx	#2
gir1_lp1:
	lda	sector_start,x
	sta	fptr_zp,x
	lda	local_start,x
	sta	eptr_zp,x
	dex
	bpl	gir1_lp1
	jmp	is_zero_range
get_inv_range2:
	ldx	#2
gir2_lp1:
	lda	local_end,x
	sta	fptr_zp,x
	lda	sector_end,x
	sta	eptr_zp,x
	dex
	bpl	gir2_lp1
is_zero_range:
	ldx	#2
izr_lp1:
	lda	fptr_zp,x
	cmp	eptr_zp,x
	bne	izr_fl1
	dex
	bpl	izr_lp1
; the pointers are equal
	sec
	rts
izr_fl1:
	clc
	rts
;**************************************************************************
;*
;* NAME  set_tmp_rptr, set_tmp_rptr_range
;*
;* DESCRIPTION
;*   set rptr from the current fptr
;*   C=1 means that the range is 0
;*
;******
set_tmp_rptr:
	lda	#0
	sta	rptr_zp
	sta	rptr_zp+1
	lda	#(TMP_START>>16) & $ff
	sta	rptr_zp+2
	rts
set_tmp_rptr_range:
	lda	fptr_zp
	sec
	sbc	sector_start
	sta	rptr_zp
	lda	fptr_zp+1
	sbc	sector_start+1
	sta	rptr_zp+1
	lda	fptr_zp+2
	sbc	sector_start+2
	clc
	adc	#(TMP_START>>16) & $ff
	sta	rptr_zp+2

	if	EXTRA_DEBUG
	jsr	print_rptr
	jsr	print_cr
	endif
	rts

this_sector:
	ds.b	1
first_sector:
	ds.b	1
last_sector:
	ds.b	1
start_ptr:
	ds.b	3
end_ptr:
	ds.b	3
buf_ptr:
	ds.b	3





;**************************************************************************
;*
;* NAME  check_empty
;*
;* DESCRIPTION
;*   start: fptr_zp, fptr_zp+1, fptr_zp+2
;*   end:   eptr_zp, eptr_zp+1, eptr_zp+2
;*   returns Acc=$ff if empty
;*
;******
check_empty:
; exit product id mode, just to be sure
 	jsr	exit_product_id

; check if the area contains just $ff
	ldy	fptr_zp
	lda	#0
	sta	fptr_zp
ce_lp1:
	jsr	cmp256_fptr_eptr ; last block?
	beq	ce_skp1		 ; yes, skip to last block check.
; check one 256 byte block by and:ing all bytes together
	jsr	read_fbyte	; read one byte to set up ptr_zp and window
ce_lp2:
	and	(ptr_zp),y
	iny
	bne	ce_lp2
	cmp	#$ff
	bne	ce_fl1
; block was empty, do the next.
	jsr	inc256_fptr
	bra	ce_lp1

; we are at the last block, less that 256 bytes left
ce_skp1:
	cpy	eptr_zp		; aligned end?
	beq	ce_ex1		; yes, exit with success

; do last block
	jsr	read_fbyte	; read one byte to set up ptr_zp and window
ce_lp3:
	and	(ptr_zp),y
	iny
	cpy	eptr_zp
	bne	ce_lp3
	cmp	#$ff
	bne	ce_fl1

ce_ex1:
; end of sector found, load Acc with $ff to flag success
	lda	#$ff
ce_fl1:
	rts

;**************************************************************************
;*
;* NAME  sector_dump
;*
;* DESCRIPTION
;*   in: Acc=sector,  rptr_zp, rptr_zp+1, rptr_zp+2
;*
;******
sector_dump:
	jsr	set_sector_addr_end
;**************************************************************************
;*
;* NAME  dump_range
;*
;* DESCRIPTION
;*   start: fptr_zp, fptr_zp+1, fptr_zp+2
;*          (rptr_zp, rptr_zp+1, rptr_zp+2)
;*   end+1: eptr_zp, eptr_zp+1, eptr_zp+2
;*   out: C=0 means ok, (C=1 means error)
;*
;******
dump_range:
	jsr	check_frange
	bcs	dpr_fl1

; exit product id mode, just to be sure
 	jsr	exit_product_id

	if	DEBUG_OUT
	lda	#<sector_dump_msg
	ldy	#>sector_dump_msg
	jsr	dbg_print
	ldy	#9
	jsr	dbg_printfptr_full
	ldy	#17
	jsr	dbg_printfptr_full
	endif
	jsr	prepare_dma

dpr_lp1:
	jsr	calc_len_fptr_eptr

; copy to nearest page end or upto eptr_zp if closer.
	lda	fptr_zp
	sta	$d300
	lda	fptr_zp+1
	sta	$d301
	lda	fptr_zp+2
	sta	$d302
	lda	rptr_zp
	sta	$d303
	lda	rptr_zp+1
	sta	$d304
	lda	rptr_zp+2
	ora	#$40
	sta	$d305
	jsr	perform_dma

; ok, increase pointers
	jsr	add_fptr_rptr
; print count
	if	DEBUG_OUT
	ldy	#17
	jsr	dbg_printfptr_full
	endif
; check if done.
	jsr	sbc_fptr_eptr
	bcc	dpr_lp1		; fptr_zp < eptr_zp

	if	DEBUG_OUT
	jsr	dbg_printcr
	endif
	jmp	err_ok
dpr_fl1:
	jmp	err_range

	if	DEBUG_OUT
sector_dump_msg:
	dc.b	"DUMPING $000000-$000000...",0
	endif

;**************************************************************************
;*
;* NAME  sector_verify
;*
;* DESCRIPTION
;*   in: Acc=sector,  rptr_zp, rptr_zp+1, rptr_zp+2
;*   out: C=0  (C=1 means failed, fptr_zp is the address)
;*
;******
sector_verify:
	jsr	set_sector_addr_end
;**************************************************************************
;*
;* NAME  verify_range
;*
;* DESCRIPTION
;*   start: fptr_zp, fptr_zp+1, fptr_zp+2
;*          (rptr_zp, rptr_zp+1, rptr_zp+2)
;*   end+1: eptr_zp, eptr_zp+1, eptr_zp+2
;*   out: C=0 means ok, (C=1 means error)
;*
;******
verify_range:
	jsr	check_frange
	bcs	vfr_fl2

; exit product id mode, just to be sure
 	jsr	exit_product_id

	if	DEBUG_OUT
	lda	#<sector_verify_msg
	ldy	#>sector_verify_msg
	jsr	dbg_print
	ldy	#11
	jsr	dbg_printfptr_full
	ldy	#19
	jsr	dbg_printfptr_full
	endif

	jsr	prepare_dma

vfr_lp1:
	jsr	calc_len_fptr_eptr

; copy from flash to buf0.
	jsr	dma_fptr_to_buf0
; copy from ram to buf1.
	jsr	dma_rptr_to_buf1

; compare buffers (len_zp is <=$0100)
	ldy	#0
vfr_lp2:
	lda	buf0,y
	cmp	buf1,y
	bne	vfr_fl1
	iny
	cpy	len_zp
	bne	vfr_lp2

; ok, increase pointers
	jsr	add_fptr_rptr
; print count
	if	DEBUG_OUT
	ldy	#19
	jsr	dbg_printfptr_full
	endif
; check if done.
	jsr	sbc_fptr_eptr
	bcc	vfr_lp1		; fptr_zp < eptr_zp

	if	DEBUG_OUT
	jsr	dbg_printcr
	endif
	jmp	err_ok

vfr_fl1:
; preserve
	lda	buf0,y
	sta	err_actual
	lda	buf1,y
	sta	err_expected
; add offset
	sty	len_zp
	lda	#0
	sta	len_zp+1
	jsr	add_fptr_rptr

	if	DEBUG_OUT
	ldy	#19
	jsr	dbg_printfptr_full
	jsr	dbg_printcr
	endif
	jmp	err_vfy
vfr_fl2:
	jmp	err_range

	if	DEBUG_OUT
sector_verify_msg:
	dc.b	"VERIFYING $000000-$000000...",0
	endif

;**************************************************************************
;*
;* NAME  sector_program
;*
;* DESCRIPTION
;*   in: Acc=sector,  rptr_zp, rptr_zp+1, rptr_zp+2
;*   out: C=0  (C=1 means failed, fptr_zp is the address, Acc is the status)
;*
;******
sector_program:
	jsr	set_sector_addr_end
;**************************************************************************
;*
;* NAME  program_range_int
;*
;* DESCRIPTION
;*   start: fptr_zp, fptr_zp+1, fptr_zp+2
;*          (rptr_zp, rptr_zp+1, rptr_zp+2)
;*   end+1: eptr_zp, eptr_zp+1, eptr_zp+2
;*   out: C=0 means ok, (C=1 means error)
;*
;******
program_range_int:
	jsr	check_wp_range
	bcs	pri_fl2

; exit product id mode, just to be sure
 	jsr	exit_product_id

	if	DEBUG_OUT
	lda	#<sector_program_msg
	ldy	#>sector_program_msg
	jsr	dbg_print
	ldy	#13
	jsr	dbg_printfptr_full
	ldy	#21
	jsr	dbg_printfptr_full
	endif

	jsr	prepare_dma
pri_lp1:
	jsr	calc_len_fptr_eptr

; copy from ram to buf1.
	jsr	dma_rptr_to_buf1

; important, no burst mode during programming.
; (mostly because it makes the timeout more complicated)
	jsr	disable_burst
; program from buff (len_zp is <=$0100)
; also, fptr_zp + len_zp within the same page
	jsr	program_block_unprot
	jsr	enable_burst
	bcs	pri_fl1

	if	SUPPORT_PROGRAM_VERIFY
; verify from buff (len_zp is <=$0100)
; also, fptr_zp + len_zp within the same page
	jsr	verify_block_raw
	bcs	pri_fl3		; verify error, Acc=read value
	endif	;SUPPORT_PROGRAM_VERIFY

; ok, increase pointers
	jsr	add_fptr_rptr
; print count
	if	DEBUG_OUT
	ldy	#21
	jsr	dbg_printfptr_full
	endif
; check if done.
	jsr	sbc_fptr_eptr
	bcc	pri_lp1		; fptr_zp < eptr_zp

	if	DEBUG_OUT
	jsr	dbg_printcr
	endif

; exit product id mode, just to be sure.
	jsr	exit_product_id
	jmp	err_ok

pri_fl1:
	jsr	read_fbyte
	jsr	pri_fixup
	jmp	err_prog
pri_fl2:
	jmp	err_wp
	if	SUPPORT_PROGRAM_VERIFY
pri_fl3:
	jsr	pri_fixup
	jmp	err_vfy
	endif	;SUPPORT_PROGRAM_VERIFY

pri_fixup:
; preserve
	sta	err_actual
	lda	buf1,y
	sta	err_expected
; add offset
	sty	len_zp
	lda	#0
	sta	len_zp+1
	jsr	add_fptr_rptr
	if	DEBUG_OUT
	ldy	#21
	jsr	dbg_printfptr_full
	jsr	dbg_printcr
	endif
; exit product id mode, just to be sure.
	jmp	exit_product_id


	if	DEBUG_OUT
sector_program_msg:
	dc.b	"PROGRAMMING $000000-$000000...",0
	endif

;**************************************************************************
;*
;* NAME  identify_flash
;*
;* DESCRIPTION
;*   Try to identify the type of flash
;*
;******
IDENT_BUF_LEN	equ	32
identify_flash:
	jsr	map_flash

; read before product id mode so we can see later if product id was entered.
	ldy	#IDENT_BUF_LEN-1
idf_lp1:
	lda	FLASH_WINDOW,y
	sta	pre_ident_buf,y
	dey
	bpl	idf_lp1

; enter product id mode
	jsr	enter_product_id

; read during product id mode
	ldy	#IDENT_BUF_LEN-1
idf_lp2:
	lda	FLASH_WINDOW,y
	sta	ident_buf,y
	dey
	bpl	idf_lp2

; exit product id and unmap flash
	jsr	unmap_flash

; check for differences
	ldy	#IDENT_BUF_LEN-1
idf_lp3:
	lda	ident_buf,y
	cmp	pre_ident_buf,y
	bne	idf_skp7	; diff, yes skip out.
	dey
	bpl	idf_lp3
; no bytes changed = no flash found
	ldx	#TYPE_NOT_FOUND
	ldy	#CONFIG_ATMEL_TOP
	bra	idf_ex1

; The data is from product id mode, check type
idf_skp7:
	ldx	#TYPE_UNKNOWN
	ldy	#CONFIG_ATMEL_TOP

	lda	id1
	cmp	#$1f		; Atmel
	beq	idf_skp3
	cmp	#$bf		; SST
	bne	idf_ex1

; SST Flashes
	lda	id2sst
	cmp	#$c8		; SST39VF1681
	bne	idf_skp4
	ldx	#TYPE_SST39VF1681
	ldy	#CONFIG_SST_UNI
idf_skp4:
	cmp	#$c9		; SST39VF1682
	bne	idf_skp5
	ldx	#TYPE_SST39VF1682
	ldy	#CONFIG_SST_UNI
idf_skp5:
	bra	idf_ex1

; Atmel Flashes
idf_skp3:
	lda	id2at
	cmp	#$c0
	bne	idf_skp1
	ldx	#TYPE_AT4XBV16X
	ldy	#CONFIG_ATMEL_BOTTOM
idf_skp1:
	cmp	#$c2		; top bootblock
	bne	idf_skp2
	ldx	#TYPE_AT4XBV16XT
	ldy	#CONFIG_ATMEL_TOP
idf_skp2:

idf_ex1:
; Select Configuration
; X=Flash Type, Y=Configuration
	stx	flash_type
	lda	config_tab,y
	sta	idf_sm1+1
	lda	config_tab+1,y
	sta	idf_sm1+2
idf_sm1:
	jsr	idf_sm1

; always set low-mem write protect on identify
	lda	#1
	sta	lowmem_wp

	jmp	err_ok

CONFIG_ATMEL_TOP	equ	0*2
CONFIG_ATMEL_BOTTOM	equ	1*2
CONFIG_SST_UNI		equ	2*2
config_tab:
	dc.w	set_atmel_top
	dc.w	set_atmel_bottom
	dc.w	set_sst_uni

; Atmel flashes top/bottom
set_atmel_bottom:
	ldy	#CONFIG_ATMEL_BOTTOM
	dc.b	$2c
set_atmel_top:
	ldy	#ADDRTAB_TOP
	jsr	set_addr_table

	lda	#<[ATMEL_SECTOR_ERASE_TIMEOUT/1000]
	sta	sector_erase_timeout
	lda	#>[ATMEL_SECTOR_ERASE_TIMEOUT/1000]
	sta	sector_erase_timeout+1

	lda	#<pb_atmelodd_prog
	sta	pb_prog_routine
	lda	#>pb_atmelodd_prog
	sta	pb_prog_routine+1
	lda	#<se_atmel_poll
	sta	se_poll_routine
	lda	#>se_atmel_poll
	sta	se_poll_routine+1

	lda	#1
	sta	have_sector_lockdown
	rts

; SST flashes
set_sst_uni:
	ldy	#ADDRTAB_UNI
	jsr	set_addr_table

	lda	#<pb_sst_prog
	sta	pb_prog_routine
	lda	#>pb_sst_prog
	sta	pb_prog_routine+1
	lda	#<se_sst_poll
	sta	se_poll_routine
	lda	#>se_sst_poll
	sta	se_poll_routine+1

	lda	#0
	sta	have_sector_lockdown
	rts

set_addr_table:
	sty	addr_table_select
	lda	addr_tab_lengths,y
	sta	num_sectors
	rts

TYPE_NOT_FOUND		equ	0
TYPE_UNKNOWN		equ	1
TYPE_AT4XBV16X		equ	2
TYPE_AT4XBV16XT		equ	3
TYPE_SST39VF1681	equ	4
TYPE_SST39VF1682	equ	5


;**************************************************************************
;*
;* SECTION  config
;*
;* DESCRIPTION
;*
;******
flash_type:
	dc.b	0

sector_erase_timeout:
	dc.w	ATMEL_SECTOR_ERASE_TIMEOUT/1000
have_sector_lockdown:
	dc.b	1
;* jump table *
	if	[.&$ff] = $ff
	echo	"broken indirect jump",.
	echo	"(adjusting)"
	dc.b	0
	endif
pb_prog_routine:
	dc.w	pb_atmelodd_prog
se_poll_routine:
	dc.w	se_atmel_poll

;**************************************************************************
;*
;* NAME  set_sector_addr, set_sector_addr_end
;*
;* DESCRIPTION
;*   Acc=sector
;*   sets target address: fptr_zp, fptr_zp+1, fptr_zp+2
;*   sets target end address: eptr_zp, eptr_zp+1, eptr_zp+2
;*
;******
set_sector_addr_end:
	pha
	clc
	adc	#1
	jsr	set_sector_addr
	lda	fptr_zp
	sta	eptr_zp
	lda	fptr_zp+1
	sta	eptr_zp+1
	lda	fptr_zp+2
	sta	eptr_zp+2
	pla
set_sector_addr:
	stx	xtmp_zp
	asl
	ldx	addr_table_select
	clc
	adc	addr_tab_offsets,x
	tax
	lda	#0
	sta	fptr_zp
	lda	addr_tables,x
	sta	fptr_zp+1
	lda	addr_tables+1,x
	sta	fptr_zp+2
	ldx	xtmp_zp
	rts

;**************************************************************************
;*
;* NAME  find_sector_num
;*
;* DESCRIPTION
;*   Source address: fptr_zp, fptr_zp+1, fptr_zp+2
;*   Returns: Acc=sector, (C=1 means not found)
;*
;******
find_sector_num:
	stx	xtmp_zp
	sty	ytmp_zp
	ldx	addr_table_select
	lda	addr_tab_offsets,x
	tax
	ldy	#0
fsn_lp1:
	lda	fptr_zp+1		; fptr_zp-next_sector_addr
	cmp	addr_tables+2,x
	lda	fptr_zp+2
	sbc	addr_tables+2+1,x
	bcc	fsn_ex1			; neg, we found the sector
fsn_skp1:
	inx
	inx
	iny
	cpy	num_sectors
	bne	fsn_lp1
; all sectors scanned, exit with error
	ldy	ytmp_zp
	ldx	xtmp_zp
	sec			; not found
	rts
fsn_ex1:
	tya
	ldy	ytmp_zp
	ldx	xtmp_zp
	clc
	rts

ADDRTAB_TOP	equ	0
ADDRTAB_BOTTOM	equ	1
ADDRTAB_UNI	equ	2

addr_table_select:
	dc.b	ADDRTAB_TOP
num_sectors:
	dc.b	39

addr_tab_offsets:
	dc.b	addr_t-addr_tables
	dc.b	addr_b-addr_tables
	dc.b	addr_u-addr_tables
addr_tab_lengths:
	dc.b	NUM_SECTORS_T
	dc.b	NUM_SECTORS_B
	dc.b	NUM_SECTORS_U

addr_tables:
; These are the high 16 bits of the 24-bit start addresses of each sector,
; for an AT49/AT47BV16xT device (Top Boot-block).
;
addr_t:
	dc.w	$0000,$0100,$0200,$0300,$0400,$0500,$0600,$0700
	dc.w	$0800,$0900,$0a00,$0b00,$0c00,$0d00,$0e00,$0f00
	dc.w	$1000,$1100,$1200,$1300,$1400,$1500,$1600,$1700
	dc.w	$1800,$1900,$1a00,$1b00,$1c00,$1d00,$1e00
	dc.w    $1f00,$1f20,$1f40,$1f60,$1f80,$1fa0,$1fc0,$1fe0
; end address to simplify length calculation
	dc.w	$2000
NUM_SECTORS_T	equ	39

; These are the high 16 bits of the 24-bit start addresses of each sector,
; for an AT49/AT47BV16x device (Bottom Boot-block).
;
addr_b:
	dc.w	$0000,$0020,$0040,$0060,$0080,$00a0,$00c0,$00e0
	dc.w	$0100,$0200,$0300,$0400,$0500,$0600,$0700
	dc.w	$0800,$0900,$0a00,$0b00,$0c00,$0d00,$0e00,$0f00
	dc.w	$1000,$1100,$1200,$1300,$1400,$1500,$1600,$1700
	dc.w	$1800,$1900,$1a00,$1b00,$1c00,$1d00,$1e00,$1f00
; end address to simplify length calculation
	dc.w	$2000
NUM_SECTORS_B	equ	39

; These are the high 16 bits of the 24-bit start addresses of each sector,
; for an SST39VF1682 device (Top Boot-block) and SST39VF1681 device (Bottom
; Boot-block)
;
addr_u:
	dc.w	$0000,$0100,$0200,$0300,$0400,$0500,$0600,$0700
	dc.w	$0800,$0900,$0a00,$0b00,$0c00,$0d00,$0e00,$0f00
	dc.w	$1000,$1100,$1200,$1300,$1400,$1500,$1600,$1700
	dc.w	$1800,$1900,$1a00,$1b00,$1c00,$1d00,$1e00,$1f00
; end address to simplify length calculation
	dc.w	$2000
NUM_SECTORS_U	equ	32


;**************************************************************************
;*
;* NAME  inc_fptr, inc256_fptr, inc_rptr, inc256_rptr,
;*       cmp_fptr_eptr,cmp256_fptr_eptr, sbc_fptr_eptr
;*
;* DESCRIPTION
;*   Helper functions for pointers
;*
;******
sbc_fptr_eptr:
	lda	fptr_zp
	cmp	eptr_zp
	lda	fptr_zp+1
	sbc	eptr_zp+1
	lda	fptr_zp+2
	sbc	eptr_zp+2
	rts

cmp_fptr_eptr:
	lda	fptr_zp
	cmp	eptr_zp
	bne	cfe_ex1
cmp256_fptr_eptr:
	lda	fptr_zp+1
	cmp	eptr_zp+1
	bne	cfe_ex1
	lda	fptr_zp+2
	cmp	eptr_zp+2
cfe_ex1:
	rts

inc_fptr:
	inc	fptr_zp
	bne	ifp_ex1
inc256_fptr:
	inc	fptr_zp+1
	bne	ifp_ex1
	inc	fptr_zp+2
ifp_ex1:
	rts

inc_rptr:
	inc	rptr_zp
	bne	irp_ex1
inc256_rptr:
	inc	rptr_zp+1
	bne	irp_ex1
	inc	rptr_zp+2
irp_ex1:
	rts

;**************************************************************************
;*
;* NAME  calc_len_fptr_eptr
;*
;* DESCRIPTION
;*   set len_zp to the distance up to the next fptr_zp page
;*   or upto eptr_zp if within the same page.
;*   i.e adding fptr_zp+len_zp will always keep within the page boundary.
;*
;******
calc_len_fptr_eptr:
	jsr	cmp256_fptr_eptr
	bne	clfe_skp1

; eptr within the same page,
; set len = eptr_zp-fptr_zp
	lda	eptr_zp
	sec
	sbc	fptr_zp
	sta	len_zp
	lda	#0
	sta	len_zp+1
	rts

clfe_skp1:
; eptr in a different page,
; set len = $0100-fptr_zp
	lda	#$00
	sec
	sbc	fptr_zp
	sta	len_zp
	lda	#$01
	sbc	#0
	sta	len_zp+1
	rts

;**************************************************************************
;*
;* NAME  add_fptr_rptr
;*
;* DESCRIPTION
;*   add len_zp to fptr_zp and rptr_zp
;*
;******
add_fptr_rptr:
	lda	fptr_zp
	clc
	adc	len_zp
	sta	fptr_zp
	lda	fptr_zp+1
	adc	len_zp+1
	sta	fptr_zp+1
	bcc	afr_skp1
	inc	fptr_zp+2
afr_skp1:

	lda	rptr_zp
	clc
	adc	len_zp
	sta	rptr_zp
	lda	rptr_zp+1
	adc	len_zp+1
	sta	rptr_zp+1
	bcc	afr_skp2
	inc	rptr_zp+2
afr_skp2:
	rts

;**************************************************************************
;*
;* NAME  prepare_dma, perform_dma
;*
;* DESCRIPTION
;*   src: $d300, $d301, $d302
;*   dest: $d303, $d304, $d305
;*   len: len_zp
;*
;******
prepare_dma:
	jsr	wait_dma
; source and dest step=1
	lda	#1
	sta	$d306
	sta	$d308
	lda	#0
	sta	$d307
	sta	$d309
	rts

; len_zp, len_zp+1 = length
perform_dma:
; set length
	lda	len_zp
	sta	$d30a
	lda	len_zp+1
	sta	$d30b
; perform dma
	lda	#%00001101	; Source Dir=pos, Dest Dir=pos, Force Start=1
	sta	$d31f
wait_dma:
pfd_lp1:
	lda	$d31f
	lsr
	bcs	pfd_lp1
; Important! Set DMA source address to RAM to stop idle fetches from
; accessing RAM.
	lda	#$40
	sta	$d302
	rts

dma_fptr_to_buf0:
	lda	fptr_zp
	sta	$d300
	lda	fptr_zp+1
	sta	$d301
	lda	fptr_zp+2
	sta	$d302
	lda	#<buf0
	sta	$d303
	lda	#>buf0
	sta	$d304
	lda	#$40
	sta	$d305
	bra	perform_dma

dma_rptr_to_buf1:
	lda	rptr_zp
	sta	$d300
	lda	rptr_zp+1
	sta	$d301
	lda	rptr_zp+2
	ora	#$40
	sta	$d302
	lda	#<buf1
	sta	$d303
	lda	#>buf1
	sta	$d304
	lda	#$40
	sta	$d305
	bra	perform_dma

;**************************************************************************
;*
;* NAME  write_fbyte
;*
;* DESCRIPTION
;*   target address: fptr_zp, fptr_zp+1, fptr_zp+2
;*   Y = offset (must be within the same $100 block)
;*   Acc = Byte to write.
;*
;******
write_fbyte:
	pha
	lda	fptr_zp+2
	sta	bank_zp
	lda	fptr_zp+1
	asl
	rol	bank_zp
	asl
	rol	bank_zp
	sac	$dd
	lda	bank_zp
	sac	$00
	lda	fptr_zp
	sta	ptr_zp
	lda	fptr_zp+1
	and	#%00111111
	ora	#>FLASH_WINDOW
	sta	ptr_zp+1
	pla

; it is absolutely crucial that we are in skip additional cycles mode
; here, otherwise an absolute STA required because the zeropage indexed one
; will generate an additional read access.
	sta	(ptr_zp),y
	rts

;**************************************************************************
;*
;* NAME  read_fbyte
;*
;* DESCRIPTION
;*   source address: fptr_zp, fptr_zp+1, fptr_zp+2
;*   Y = offset (must be within the same $100 block)
;*   Acc = Byte read from flash.
;*
;******
read_fbyte:
	lda	fptr_zp+2
	sta	bank_zp
	lda	fptr_zp+1
	asl
	rol	bank_zp
	asl
	rol	bank_zp
	sac	$dd
	lda	bank_zp
	sac	$00
	lda	fptr_zp
	sta	ptr_zp
	lda	fptr_zp+1
	and	#%00111111
	ora	#>FLASH_WINDOW
	sta	ptr_zp+1
	lda	(ptr_zp),y
	rts

;**************************************************************************
;*
;* NAME  write_rbyte
;*
;* DESCRIPTION
;*   target address: rptr_zp, rptr_zp+1, rptr_zp+2
;*   Y = offset (must be within the same $100 block)
;*   Acc = Byte to write.
;*
;******
write_rbyte:
	pha
	lda	rptr_zp+2
	sta	bank_zp
	lda	rptr_zp+1
	asl
	rol	bank_zp
	asl
	rol	bank_zp
	sac	$ee
	lda	bank_zp
	sac	$00
	lda	rptr_zp
	sta	ptr2_zp
	lda	rptr_zp+1
	and	#%00111111
	ora	#>RAM_WINDOW
	sta	ptr2_zp+1
	pla
	sta	(ptr2_zp),y
	rts

;**************************************************************************
;*
;* NAME  read_rbyte
;*
;* DESCRIPTION
;*   source address: rptr_zp, rptr_zp+1, rptr_zp+2
;*   Y = offset (must be within the same $100 block)
;*   Acc = Byte read from flash.
;*
;******
read_rbyte:
	lda	rptr_zp+2
	sta	bank_zp
	lda	rptr_zp+1
	asl
	rol	bank_zp
	asl
	rol	bank_zp
	sac	$ee
	lda	bank_zp
	sac	$00
	lda	rptr_zp
	sta	ptr2_zp
	lda	rptr_zp+1
	and	#%00111111
	ora	#>RAM_WINDOW
	sta	ptr2_zp+1
	lda	(ptr2_zp),y
	rts

;**************************************************************************
;*
;* NAME  program_byte
;*
;* DESCRIPTION
;*
;******
program_byte:
	jsr	check_wp
	bcs	pb_fl3

; important, no burst mode during programming.
	jsr	disable_burst

	ldy	#0
	sty	len_zp+1
	iny
	sty	len_zp
	sta	buf1
	jsr	program_block_unprot
	bcs	pb_fl1		; programming error
	jsr	verify_block_raw
	bcs	pb_fl2		; verify error, Acc=read value

; reenable burst.
	jsr	enable_burst
	jmp	err_ok
pb_fl1:
	jsr	read_fbyte
	jsr	pb_fixup
	jmp	err_prog
pb_fl2:
	jsr	pb_fixup
	jmp	err_vfy
pb_fl3:
	jmp	err_wp


pb_fixup:
	sta	err_actual
	lda	buf1
	sta	err_expected
; reenable burst.
	jmp	enable_burst

;**************************************************************************
;*
;* NAME  program_block_unprot
;*
;* DESCRIPTION
;*   program from buf1 (len_zp is <=$0100)
;*   fptr_zp + len_zp must be within the same page
;*
;*   In: fptr_zp=start addr
;*       len_zp=length ($00 = 256)
;*   Out: C=0 OK.
;* 	  C=1, Fail. Y=offset
;*
;******
program_block_unprot:
	lda	fptr_zp+2
	sta	bank_zp
	lda	fptr_zp+1
	asl
	rol	bank_zp
	asl
	rol	bank_zp
	lda	fptr_zp
	sta	ptr_zp
	lda	fptr_zp+1
	and	#%00111111
	ora	#>FLASH_WINDOW
	sta	ptr_zp+1

	ldy	#0
	jmp	(pb_prog_routine)

;*********************
;* Atmel trace debug macro
;*
	mac	ATMEL_TRACE
	lda	(ptr_zp),y
	sta	$c000
	lda	(ptr_zp),y
	sta	$c001
	lda	(ptr_zp),y
	sta	$c002
	lda	(ptr_zp),y
	sta	$c003
	lda	(ptr_zp),y
	sta	$c004
	lda	(ptr_zp),y
	sta	$c005
	lda	(ptr_zp),y
	sta	$c006
	lda	(ptr_zp),y
	sta	$c007
	lda	(ptr_zp),y
	sta	$c008
	lda	(ptr_zp),y
	sta	$c009
	lda	(ptr_zp),y
	sta	$c00a
	lda	(ptr_zp),y
	sta	$c00b
	lda	(ptr_zp),y
	sta	$c00c
	lda	(ptr_zp),y
	sta	$c00d
	lda	(ptr_zp),y
	sta	$c00e
	lda	(ptr_zp),y
	sta	$c00f
	tya
	eor	ptr_zp
	and	#1
	beq	pbatd_even
	lda	$c000
	eor	tmp_zp
	and	#$80
	bne	pbatd_busy
	lda	tmp_zp
	sta	$c010
	lda	fptr_zp
	sta	$c012
	lda	fptr_zp+1
	sta	$c013
	lda	fptr_zp+2
	sta	$c014
	sty	$c015
	php
	pla
	sta	$c016
	ldx	#$1f
pbatd_lp2:
	inc	$d020
	lda	$c000,x
pbatd_sm1:
	sta	$e000,x
	dex
	bpl	pbatd_lp2
	lda	pbatd_sm1+1
	clc
	adc	#$20
	sta	pbatd_sm1+1
	bcc	pbatd_ex1
	inc	pbatd_sm1+2
	bne	pbatd_ex1
pbatd_lp1:
	inc	$d020
	bra	pbatd_lp1
pbatd_ex1:
pbatd_busy:
pbatd_even:
	lda	tmp_zp
	sta	$c011
	endm

pb_atmelodd_prog:
;*********************
;* Atmel Odd byte hack prog Mode
;*
pbao_lp1:
	sir	$d2
	ldy	#$00
	lda	#$aa
	sta	FLASH_WINDOW+FLASH_OFFS_555
	lda	#$55
	sta	FLASH_WINDOW+FLASH_OFFS_AAA
	lda	#$a0
	sta	FLASH_WINDOW+FLASH_OFFS_555

	ldy	bank_zp
	sir	$12
	lda	buf1,y
	sta	(ptr_zp),y
	sta	tmp_zp

	if	ATMEL_TRACE_DEBUG
	ATMEL_TRACE
	endif	;ATMEL_TRACE_DEBUG
pb_atmelodd_poll:
	CDEBUG	7
; The AT47BV161x is very strange. Programming odd bytes always timeout and
; enter the error state but usually works anyway.
; The data polling read out is not always correct, and sometimes it does
; not toggle properly.
; This could be due to some part of the DTV reading the flash but most is
; disabled (char fetch, dma idle).
; If something is still there my guess is that it would be the VIC-II
; emulation, or the read timing on the bus.
;
; we work around this problem by trying to force exit program mode, and then
; requiring 4 correct reads.  It seems that exiting program mode is just
; ignored until the programming is done.
  	ldx	#ATMEL_ODD_BYTE_HACK_TIMEOUT/19
pbao_lp2:

; Time-out... exit program mode.
	lda	#$f0		; 2
	sta	FLASH_WINDOW	; 4

; check if data was correct anyway.
	lda	(ptr_zp),y	; 5
	cmp	tmp_zp		; 3
	bne	pbao_skp1	; not yet.
	lda	(ptr_zp),y	; 5
	cmp	tmp_zp		; 3
	bne	pbao_skp1	; not correct the second time
	lda	(ptr_zp),y	; 5
	cmp	tmp_zp		; 3
	bne	pbao_skp1	; not correct 3 times.
	lda	(ptr_zp),y	; 5
	cmp	tmp_zp		; 3
	beq	pbao_ex1	; 2	; yes, programming worked

pbao_skp1:
; if still failed, retry exit + check for the maximum programming time
	dex			; 1
	bne	pbao_lp2	; 2
				; fastest path ~19 (not critical)
	CDEBUG	2
; flag failure and exit
	sec
	jmp	exit_product_id

pbao_ex1:
	if	ATMEL_TIMEOUT_DEBUG
	cpx	$0805
	bcs	pbao_skp2
	stx	$0805
pbao_skp2:
	ldx	#ATMEL_ODD_BYTE_HACK_TIMEOUT/19
	stx	$0806
	endif	;ATMEL_TIMEOUT_DEBUG
	CDEBUG	5
	iny
	cpy	len_zp
	bne	pbao_lp1

	CDEBUG	6
; flag success and exit
	clc
	jmp	exit_product_id

pb_sst_prog:
;*********************
;* SST Prog Mode
;*
pbs_lp1:
	sir	$d2
	ldy	#$00
	lda	#$aa
	sta	FLASH_WINDOW+FLASH_OFFS_555
	lda	#$55
	sta	FLASH_WINDOW+FLASH_OFFS_AAA
	lda	#$a0
	sta	FLASH_WINDOW+FLASH_OFFS_555

	ldy	bank_zp
	sir	$12
	lda	buf1,y
	sta	(ptr_zp),y
	sta	tmp_zp		; 3

	ldx	#SST_PROG_BYTE_TIMEOUT 	; 2
; poll status
pbs_lp2:
	lda	(ptr_zp),y	; 3 cycles before performing the read
				; =8 cycles(~usecs), nominal prog =7 us.
				; only very few byte will fail the first
				; round.
	eor	tmp_zp
	asl			; C=MSB ^ MSB of expected byte.
	bcc	pbs_ex1		; C=0 (equal), yes, exit

	dex
	bne	pbs_lp2

; flag failure and exit
	sec
	jmp	exit_product_id

pbs_ex1:
	iny
	cpy	len_zp
	bne	pbs_lp1
; flag success and exit
	clc
	jmp	exit_product_id

;**************************************************************************
;*
;* NAME  verify_block_raw
;*
;* DESCRIPTION
;*   verify with buf1 (len_zp is <=$0100)
;*   fptr_zp + len_zp must be within the same page
;*   assumes that bank_zp has been setup already (using program_block_unprot)
;*
;*   In: fptr_zp=start addr
;*       len_zp=length ($00 = 256)
;*   Out: C=0 OK.
;* 	  C=1, Fail.  Acc=read byte, Y=offset
;*
;******
verify_block_raw:
	ldy	#0
	sir	$d2
	ldy	bank_zp
	sir	$12
vb_lp1:
	lda	(ptr_zp),y
	cmp	buf1,y
	bne	vb_fl1
	iny
	cpy	len_zp
	bne	vb_lp1
	clc
	rts
vb_fl1:
	sec
	rts

;**************************************************************************
;*
;* NAME  sector_erase
;*
;* DESCRIPTION
;*   erase sector, Acc=sector_num
;*
;******
sector_erase:
	jsr	set_sector_addr_end
	jsr	check_wp
	bcs	se_fl1

; important, no burst mode during programming.
; (mostly because it makes the timeout more complicated)
	jsr	disable_burst

; exit product id mode, just to be sure
 	jsr	exit_product_id

	if	DEBUG_OUT
	lda	#<sector_erase_msg
	ldy	#>sector_erase_msg
	jsr	dbg_print
	ldy	#16
	jsr	dbg_printfptr_full
	ldy	#24
	jsr	dbg_printeptr_full
	jsr	dbg_printcr
	endif

	sac	$dd
	lda	#$00
	sac	$00

	lda	#$aa
	sta	FLASH_WINDOW+FLASH_OFFS_555
	lda	#$55
	sta	FLASH_WINDOW+FLASH_OFFS_AAA
	lda	#$80
	sta	FLASH_WINDOW+FLASH_OFFS_555
	lda	#$aa
	sta	FLASH_WINDOW+FLASH_OFFS_555
	lda	#$55
	sta	FLASH_WINDOW+FLASH_OFFS_AAA

	lda	#$30
	ldy	#0
	jsr	write_fbyte

	jmp	(se_poll_routine)

se_fl1:
	jmp	err_wp

;*********************
;* Atmel Poll Mode
;*
se_atmel_poll:
; poll status
sea_lp1:
	lda	(ptr_zp),y
	asl			; MSB = 1?
	bcs	sea_ex1		; Yes, done.
	lsr
	and	#%00101000
	beq	sea_lp1

	lda	(ptr_zp),y
	asl			; MSB = 1?
	bcs	sea_ex1		; Yes, done

;** failure exit
	jsr	exit_product_id
	jsr	enable_burst
; flag failure and exit
	jmp	err_erase

;** normal exit
sea_ex1:
	jsr	exit_product_id
	jsr	enable_burst
; flag success and exit
	jmp	err_ok


;*********************
;* SST Poll Mode
;*
se_sst_poll:
	ldx	#SST_SECTOR_ERASE_TIMEOUT/1000 ; in milliseconds
; poll status
ses_lp1:
	lda	(ptr_zp),y
	asl			; MSB = 1?
	bcs	ses_ex1		; yes, done!

	jsr	wait_ms
	dex
	bne	ses_lp1

;** failure exit
	jsr	exit_product_id
	jsr	enable_burst
; flag failure and exit
	jmp	err_erase

;** normal exit
ses_ex1:
	jsr	exit_product_id
	jsr	enable_burst
; flag success and exit
	jmp	err_ok

	if	DEBUG_OUT
sector_erase_msg:
	dc.b	"ERASING SECTOR $000000-$000000...",0
	endif

;**************************************************************************
;*
;* NAME  sector_lockdown
;*
;* DESCRIPTION
;*   lockdown sector, Acc=sector_num
;*
;******
sector_lockdown:
	jsr	set_sector_addr
	jsr	check_wp
	bcs	sl_fl1

; important, no burst mode during programming.
	jsr	disable_burst

; exit product id mode, just to be sure
 	jsr	exit_product_id

	sac	$dd
	lda	#$00
	sac	$00

	lda	#$aa
	sta	FLASH_WINDOW+FLASH_OFFS_555
	lda	#$55
	sta	FLASH_WINDOW+FLASH_OFFS_AAA
	lda	#$80
	sta	FLASH_WINDOW+FLASH_OFFS_555
	lda	#$aa
	sta	FLASH_WINDOW+FLASH_OFFS_555
	lda	#$55
	sta	FLASH_WINDOW+FLASH_OFFS_AAA

	lda	#$60
	ldy	#0
	jsr	write_fbyte

; wait minimum 200us for lockdown to be activated
	jsr	wait_ms

; reenable burst.
	jsr	enable_burst
	jmp	err_ok
sl_fl1:
	jmp	err_wp

;**************************************************************************
;*
;* NAME  enter_product_id
;*
;* DESCRIPTION
;*   map flash bank 0
;*   enter product id mode
;*
;******
enter_product_id:
	sac	$dd
	lda	#$00
	sac	$00

	lda	#$aa
	sta	FLASH_WINDOW+FLASH_OFFS_555
	lda	#$55
	sta	FLASH_WINDOW+FLASH_OFFS_AAA
	lda	#$90
	sta	FLASH_WINDOW+FLASH_OFFS_555
	rts

;**************************************************************************
;*
;* NAME  enter_cfi_query_mode
;*
;* DESCRIPTION
;*   map flash bank 0
;*   enter cfi mode
;*     C=0 means ok, Acc=stride.
;*     C=1 means failed.
;*
;******
enter_cfi_query_mode:
	sac	$dd
	lda	#$00
	sac	$00

; First test using a normal query
	lda	#$98
	sta	FLASH_WINDOW+FLASH_OFFS_555

	jsr	check_cfi	; Did it work?
	bcc	ecqm_ex1	; Yes, skip out with C=0

; no, exit and try again
	lda	#$f0
	sta	FLASH_WINDOW

; SST style query.
	lda	#$aa
	sta	FLASH_WINDOW+FLASH_OFFS_555
	lda	#$55
	sta	FLASH_WINDOW+FLASH_OFFS_AAA
	lda	#$98
	sta	FLASH_WINDOW+FLASH_OFFS_555

	jsr	check_cfi	; Did it work? C=0 means yes.
ecqm_ex1:
	rts

check_cfi:
; stride=1
	lda	FLASH_WINDOW+$10
	cmp	#"Q"
	bne	cc_skp1
	lda	FLASH_WINDOW+$11
	cmp	#"R"
	bne	cc_skp1
	lda	FLASH_WINDOW+$12
	cmp	#"Y"
	bne	cc_skp1
	lda	#1
	clc
	rts
cc_skp1:
; stride=2
	lda	FLASH_WINDOW+$10*2
	cmp	#"Q"
	bne	cc_fl1
	lda	FLASH_WINDOW+$11*2
	cmp	#"R"
	bne	cc_fl1
	lda	FLASH_WINDOW+$12*2
	cmp	#"Y"
	bne	cc_fl1
	lda	#2
	clc
	rts
cc_fl1:
	sec
	rts

;**************************************************************************
;*
;* NAME  exit_product_id
;*
;* DESCRIPTION
;*   map flash bank 0
;*   exit product id mode
;*
;******
exit_product_id:
	sac	$dd
	lda	#$00
	sac	$00

	lda	#$f0
	sta	FLASH_WINDOW
	rts

;**************************************************************************
;*
;* NAME  mirror_roms
;*
;* DESCRIPTION
;*   Relocate charset to ram at $3800-$4000.
;*   Copy basic into ram $PPa000-$PPbfff.
;*   Copy kernal into ram $PPe000-$PPffff.
;*
;******
mirror_roms:
	sei
; move charset to a safe location
	lda	#$03
	sta	$01
; $d000 -> $3800 ($08 pages)
	lda	#$d0
	ldy	#CHARSET_PAGE
	ldx	#$08
	jsr	mr_copy
	lda	#$07
	sta	$01

; move kernal to ram
	sac	$dd
	lda	#MIRROR_PAGE*4 + $03 ; map $PPc000-$PPffff onto $4000-$7fff
	sac	$00
; $e000 -> $6000 ($20 pages)
	lda	#$e0
	ldy	#$60
	ldx	#$20
	jsr	mr_copy

; move basic to ram
	sac	$dd
	lda	#MIRROR_PAGE*4 + $02 ; map $PP8000-$PPbfff onto $4000-$7fff
	sac	$00
; $a000 -> $6000 ($20 pages)
	lda	#$a0
	ldy	#$60
	ldx	#$20
	jsr	mr_copy

; map out kernal and basic
	sac	$dd
	lda	#2		; map $004000-$008000 onto $4000-$8000
	sac	$00

	lda	#1
	sta	$d03f
	lda	#$40 | MIRROR_PAGE
	sta	$d100
	sta	$d101
	lda	#0
	sta	$d03f

; wait for a new frame
	jsr	wait_wb
; enable new charset
	lda	#%00010000 | ((CHARSET_PAGE / 8) * 2)
	sta	$d018
	cli
	rts

; copy Acc=MSB of src, Y=MSB of dest, X=num pages
mr_copy:
	sta	ptr_zp+1
	sty	ptr2_zp+1
	ldy	#0
	sty	ptr_zp
	sty	ptr2_zp
mrc_lp1:
	lda	(ptr_zp),y
	sta	(ptr2_zp),y
	iny
	bne	mrc_lp1
	inc	ptr_zp+1
	inc	ptr2_zp+1
	dex
	bne	mrc_lp1
	rts

;**************************************************************************
;*
;* NAME  unmirror_roms
;*
;* DESCRIPTION
;*   Restore charset and kernal + basic to normal.
;*
;******
unmirror_roms:
	sei

; map back the original mem
	lda	#$07
	sta	$01

; map back the original kernal
	lda	#1
	sta	$d03f
	lda	#$00
	sta	$d100
	sta	$d101
	lda	#0
	sta	$d03f

; wait for a new frame
	jsr	wait_wb
; restore charset
	lda	#%00010100
	sta	$d018

	cli
	rts

;**************************************************************************
;*
;* NAME  map_flash
;*
;* DESCRIPTION
;*   Map flash at $4000-$8000
;*
;******
map_flash:
	sei
	php
	pha

; enable extended features
	lda	#1
	sta	$d03f
; disable badlines
	lda	#%00100000
	sta	$d03c

; Important! Set DMA source address to RAM to stop idle fetches from
; accessing RAM.
	lda	#$40
	sta	$d302
; set the destination aswell, for good measure.
	sta	$d305

; burst enable, skip internal cycle
	sac	$99
	lda	#%00000011
	sac	$00

; map in flash, bank 0 at $4000
	sac	$88
	lda	#%01010001
	sac	$dd
	lda	#$00
	sac	$00

; exit product id mode, just to be sure
 	jsr	exit_product_id

; restore and exit
	pla
	plp
	rts

enable_burst:
; burst enable, skip internal cycle
	sac	$99
	lda	#%00000011
	sac	$00
	rts

disable_burst:
; burst disable, skip internal cycle
	sac	$99
	lda	#%00000001
	sac	$00
	rts

;**************************************************************************
;*
;* NAME  unmap_ram
;*
;* DESCRIPTION
;*   restore ram at $8000-$a000
;*
;******
unmap_ram:
; map in ram, bank 2 at $8000
	sac	$ee
	lda	#$02
	sac	$00
	rts

;**************************************************************************
;*
;* NAME  unmap_flash
;*
;* DESCRIPTION
;*   restore ram mapping.
;*
;******
unmap_flash:
	php
	pha

; exit product id mode, just to be sure
 	jsr	exit_product_id

; map in ram, bank 1 at $4000, and bank 2 at $8000
	sac	$88
	lda	#%01010101
	sac	$dd
	lda	#$01
	sac	$ee
	lda	#$02
	sac	$00

; disable burst, do not skip internal cycles anymore.
	sac	$99
	lda	#%00000000
	sac	$00

; enable badlines again
	lda	#%00000000
	sta	$d03c

; disable extended features
	lda	#0
	sta	$d03f

; restore and exit
	pla
	plp
	cli
	rts

;**************************************************************************
;*
;* NAME  wait_ms
;*
;* DESCRIPTION
;*   wait for ~ a millisecond (in skip cycle mode)
;*
;******
wait_ms:
	pha			; 3
	txa			; 1
	pha			; 3
	ldx	#250		; 2
wms_lp1:
	nop			; 1
	dex			; 1
	bne	wms_lp1		; 2
	pla			; 3
	tax			; 1
	pla			; 3
	rts

;**************************************************************************
;*
;* NAME  wait_wb
;*
;* DESCRIPTION
;*   wait for vertical blanking
;*
;******
wait_wb:
ww_lp1:
	lda	$d011
	bpl	ww_lp1
ww_lp2:
	lda	$d011
	bmi	ww_lp2
	rts


	seg	data
;**************************************************************************
;*
;* SECTION  data
;*
;******
	seg.u	bss
;**************************************************************************
;*
;* SECTION  bss
;*
;******
ident_buf:
	ds.b	IDENT_BUF_LEN
id1	equ	ident_buf+0*2
id2at	equ	ident_buf+1*2
id2sst	equ	ident_buf+1
id3at	equ	ident_buf+3*2
pre_ident_buf:
	ds.b	IDENT_BUF_LEN

buf0:
	ds.b	256
buf1:
	ds.b	256

; eof

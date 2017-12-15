; zeropage.asm
;
; define zero page locations

	seg.u	zp
	org	$a3
len_zp:
	ds.b	2
tmpptr_zp:
	ds.b	3
rawmode_zp:
	ds.b	1
tmp3_zp:
	ds.b	1

	org	$b0
fptr_zp:
	ds.b	3
eptr_zp:
	ds.b	3
bank_zp:
	ds.b	1

	org	$bd
tmp_zp:
	ds.b	1
tmp2_zp:
	ds.b	1

	org	$f7
xtmp_zp:
	ds.b	1
ytmp_zp:
	ds.b	1
ptr_zp:
	ds.w	1
ptr2_zp:
	ds.w	1
rptr_zp:
	ds.b	3

; seg_begin.asm
;
; start markers

	seg	data
	org	code_end

	seg.u	bss
	org	data_end

	seg	code
	org	$1000

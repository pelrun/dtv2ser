; dtv.asm
;
; define extra opcodes for DTV

	processor 6502

	MAC	sac
	dc.b	$32,{1}
	ENDM
	MAC	sir
	dc.b	$42,{1}
	ENDM
	MAC	bra
_TMPBRA	set	{1}-2-.
	if	_TMPBRA < -128 || _TMPBRA > 127
	ERR 	"Branch to long!"
	endif
	dc.b	$12,_TMPBRA
	ENDM

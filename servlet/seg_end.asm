; seg_end.asm
;
; align segments: code, data, bss

        seg     code
code_end        equ     .
        seg     data
data_end        equ     .
        seg.u   bss
bss_end         equ     .

        echo    "end",bss_end

README.txt
----------

This directory contains the assembler source code for 'servlets' that run on
the DTV. A servlet is first downloaded to the DTV memory and then a sys call
is launched.

You need the DASM assembler to build the source:
http://dasm-dillon.sourceforge.net/

The following servlets are available:

 * diag_srv.asm
   
   a small test program used for the diag sys command.
   
   org: 0x1000
   in:  ACC=<number of frames to execute>
   out: ACC=42
        XR=<number of frames to execute>
        YR=0

 * flash_srv.asm
 
   a helper for the flash operations.
   
   the source includes flash_io.asm written by Daniel Kahlin/TLR
   and was taken from his flash-1.0.zip source distribution.
   see: http://www.kahlin.net/daniel/dtv/flash.php
   
   commands in servlet:

   id:  identify flash
   org: 0x1000
   in:  -
   out: ACC = flash type

   id:  generate flash map
	 org: 0x1003
	 in:  -
	 out: 0x2000-0x2800  flash map in ASCII
   
   id:  flash operation
   org: 0x1006
   in:  ACC = mode (0=erase 1=program 2=verify 3=check_empty)
        0x2000-0x2002: <start lsb>,<start csb>,<start msb>
        0x2003-0x2005: <end lsb>,<end csb>,<end lsb>
   out: ACC = error (0=ok)
        XR  = check_empty_result ($ff=empty)

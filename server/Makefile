#
# Makefile - dtv2ser mcu makefile
#
# Written by
#  Christian Vogelgsang <chris@vogelgsang.org>
#
# This file is part of dtv2ser.
# See README for copyright notice.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
#  02111-1307  USA.
#

# ----- Config Options -----

# install dir of avr libc (here MacPorts location)
AVRLIBC_DIR = /opt/local/avr

ALL_BOARDS= cvm8board ctboard arduino2009 arduinonano
DIST_BOARDS= cvm8board arduino2009

# select board
BOARD ?= arduino2009
DEFINES ?= USE_DIAGNOSE USE_BOOT USE_JOYSTICK #USE_BLOCKCMD

ifeq "$(BOARD)" "cvm8board"

MCU = atmega8
F_CPU = 14745600
MAX_SIZE = 7168
UART_BAUD = 230400

LDR_PROG = stk500v2
LDR_SPEED = 115200

else
ifeq "$(BOARD)" "ctboard"
# see http://www.heise.de/ct/projekte/c-t-COM-auf-LAN-Adapter-284121.html

MCU = atmega8535
F_CPU = 14745600
MAX_SIZE = 65536
UART_BAUD = 230400

else
ifeq "$(BOARD)" "arduino2009"

MCU = atmega328
F_CPU = 16000000
MAX_SIZE = 30720
UART_BAUD = 250000
DEFINES += IGNORE_RTS #BLUETOOTH

LDR_PROG = arduino
LDR_SPEED = 19200

else

$(error "Unsupported board '$(BOARD)'. Only $(ALL_BOARDS) allowed!")

endif
endif
endif

# ----- End of Config -----

# mainfile/project name
PROJECT = dtv2ser
VERSION_MAJ = 0
VERSION_MIN = 5

# combine version
VERSION=$(VERSION_MAJ).$(VERSION_MIN)

# basename of output
BASENAME = $(PROJECT)-$(VERSION)-$(UART_BAUD)-$(BOARD)-$(MCU)
# project
OUTPUT = $(OUTDIR)/$(BASENAME)

# source files
SRC := $(BOARD).c
SRC += util.c uart.c uartutil.c timer.c display.c param.c
SRC += transfer.c sertrans.c dtvlow.c dtvtrans.c joy.c boot.c
SRC += cmdline.c cmdtable.c command.c
SRC += transfercmd.c paramcmd.c joycmd.c
SRC += main.c

# output format
FORMAT = ihex

# build directory
BUILD = BUILD
OBJDIR = $(BUILD)/$(BASENAME)/obj
DEPDIR = $(OBJDIR)
OUTDIR = $(BUILD)

# target files
OBJ = $(patsubst %.c,$(OBJDIR)/%.o,$(SRC))

# compiler switches
CFLAGS = -g -std=gnu99
CFLAGS += -Os
#CFLAGS += -funsigned-char -funsigned-bitfields -fpack-struct -fshort-enums
CFLAGS += -Wall -Werror -Wstrict-prototypes
CFLAGS += -I$(AVRLIBC_DIR)/include
CFLAGS += -mmcu=$(MCU) -I.

CFLAGS_LOCAL = -Wa,-adhlns=$(<:%.c=$(OBJDIR)/%.lst)
CFLAGS_LOCAL += -Wp,-M,-MP,-MT,$(OBJDIR)/$(*F).o,-MF,$(DEPDIR)/$(@F:.o=.d)
CFLAGS_LOCAL += -DVERSION_MIN="$(VERSION_MIN)" -DVERSION_MAJ="$(VERSION_MAJ)"
CFLAGS_LOCAL += -DVERSION="\"$(VERSION)\"" -DHAVE_$(BOARD) -DUART_BAUD=$(UART_BAUD)
CFLAGS_LOCAL += -DF_CPU=$(F_CPU)
CFLAGS_LOCAL += $(patsubst %,-D%,$(DEFINES))

# linker switches
LDFLAGS = -Wl,-Map=$(OUTPUT).map,--cref
LDFLAGS = -lm -lc

# Define programs and commands.
SHELL = sh
CC = avr-gcc
OBJCOPY = avr-objcopy
OBJDUMP = avr-objdump
SIZE = avr-size
NM = avr-nm
AVRDUDE = avrdude
REMOVE = rm -f
COPY = cp
RANLIB = avr-ranlib
AR = avr-ar

# define V to see compile output
ifdef V
HIDE=
else
HIDE=@
endif

# ---------- RULES ----------

help:
	@echo
	@echo "  supported boards: $(ALL_BOARDS)"
	@echo
	@echo "--- flash bootloader and program fuses ---"
	@echo "  (initial setup of device - only cvm8board!)"
	@echo
	@echo "  > make prog_bootloader"
	@echo "  > make prog_fuse"
	@echo
	@echo "    add ISP_PROG=<programmer>      (e.g. usbasp, see avrdude manual)"
	@echo "    and ISP_PORT='-P <device>'     to configure your ISP"
	@echo
	@echo "--- flash firmware ---"
	@echo "  (update firmware)"
	@echo
	@echo "  > make prog_cvm8board LDR_PORT=<serial port>"
	@echo "  > make prog_arduino2009 LDR_PORT=<serial port>"
	@echo "         flash the named board attached to given serial port"
	@echo
	@echo "--- build own firmware ---"
	@echo
	@echo "  > make build BOARD=<boardname>   build firmware for one device"
	@echo "  > make build_all                 build firmware for all devices"
	@echo

dirs:
	@if [ ! -d $(BUILD) ]; then mkdir -p $(BUILD); fi
	@if [ ! -d $(OBJDIR) ]; then mkdir -p $(OBJDIR); fi
	@if [ ! -d $(DEPDIR) ]; then mkdir -p $(DEPDIR); fi
	@if [ ! -d $(OUTDIR) ]; then mkdir -p $(OUTDIR); fi

build: dirs hdr hex size

hdr:
	@echo "--- building BOARD=$(BOARD) F_CPU=$(F_CPU) MCU=$(MCU) ---"
	@echo "             UART_BAUD=$(UART_BAUD) DEFINES=$(DEFINES)"

elf: $(OUTPUT).elf $(OUTPUT).lss $(OUTPUT).sym
	@echo "  --- resulting elf ---"
	$(HIDE)$(SIZE) $(OUTPUT).elf

hex: $(OUTPUT).hex

size: $(OUTPUT).hex
	@SIZE=`$(SIZE) -A --target=$(FORMAT) $(OUTPUT).hex | grep Total | awk '{ print $$2 }'` ; \
	if [ $$SIZE -gt $(MAX_SIZE) ] ; then \
		echo "  $$SIZE >  $(MAX_SIZE) bytes: TOO LARGE" ; exit 1 ; \
	else \
		echo "  $$SIZE <= $(MAX_SIZE) bytes: ok" ; \
	fi

clean:
	rm -rf $(BUILD)

clean_dist: clean
	rm -rf flash

build_all: clean
	@for a in $(DIST_BOARDS) ; do \
		$(MAKE) build BOARD=$$a ;\
	done

dist: build_all
	@rm -rf flash
	@mkdir flash
	@cp $(BUILD)/*.hex flash/
	@rm -rf $(BUILD)
	@ls -la flash/

# ----- Helper Rules -----

# final hex (flash) file from elf
%.hex: %.elf
	@echo "  making hex $@"
	$(HIDE)$(OBJCOPY) -O $(FORMAT) -j .data -j .text $< $@

# finale eeprom file from elf
%.eep: %.elf
	@echo "  making eep $@"
	$(HIDE)$(OBJCOPY) -j .eeprom --change-section-lma .eeprom=0 -O $(FORMAT) $< $@

# extended listing file
%.lss: %.elf
	@echo "  generating listing $@"
	$(HIDE)$(OBJDUMP) -h -S $< > $@

# Create a symbol table from ELF output file.
%.sym: %.elf
	@echo "  generating symbols $@"
	$(HIDE)$(NM) -n $< > $@

# link
%.elf: $(OBJ)
	@echo "  linking elf $@"
	$(HIDE)$(CC) $(CFLAGS) $(OBJ) --output $@ $(LDFLAGS)

# compile
$(OBJDIR)/%.o : %.c
	@echo "  compiling $<"
	$(HIDE)$(CC) -c $(CFLAGS) $(CFLAGS_LOCAL) $< -o $@

# include dependencies
-include $(shell mkdir -p $(DEPDIR) 2>/dev/null) $(wildcard $(DEPDIR)/*.d)

.PRECIOUS: $(OBJ)
.PHONY: all dirs elf hex prog clean avrlib clean.edit hdr


# ----- AVRdude --------------------------------------------------------------

LDR_PORT ?= $(shell ls /dev/cu.usbserial-*)

# ISP programmer setup
ISP_PROG ?= usbasp

# commands
AVRDUDE_WRITE_FLASH  = -U flash:w:$(OUTPUT).hex
AVRDUDE_WRITE_EEPROM = -U eeprom:w:$(OUTPUT).eep
AVRDUDE_WRITE_FUSE   = -U lfuse:w:$(LFUSE_$(MCU)):m -U hfuse:w:$(HFUSE_$(MCU)):m

AVRDUDE_ISP_FLAGS = -p $(MCU) $(ISP_EXTRA) -c $(ISP_PROG)
AVRDUDE_LDR_FLAGS = -p $(MCU) -P $(LDR_PORT) -b $(LDR_SPEED) -c $(LDR_PROG)

ifdef AVRDUDE_DEBUG
AVRDUDE_ISP_FLAGS += -v -v -v -v
AVRDUDE_LDR_FLAGS += -v -v -v -v
endif

# define fuses
LFUSE_atmega644 := 0xf7
HFUSE_atmega644 := 0xd9

# ----- atmega 8 -----
# Fuse high byte:
# 0xca = 1 1 0 0   1 0 1 0 <-- BOOTRST (boot reset vector at boot code)
#        ^ ^ ^ ^   ^ ^ ^------ BOOTSZ0 (512 words for bootloader)
#        | | | |   | +-------- BOOTSZ1
#        | | | |   + --------- EESAVE (don't preserve EEPROM over chip erase)
#        | | | +-------------- CKOPT (full output swing)
#        | | +---------------- SPIEN (allow serial programming)
#        | +------------------ WDTON (WDT not always on)
#        +-------------------- RSTDISBL (reset pin is enabled)
# Fuse low byte:
# 0x9f = 1 0 0 1   1 1 1 1
#        ^ ^ \ /   \--+--/
#        | |  |       +------- CKSEL 3..0 (external >8M crystal)
#        | |  +--------------- SUT 1..0 (crystal osc, BOD enabled)
#        | +------------------ BODEN (BrownOut Detector enabled)
#        +-------------------- BODLEVEL (2.7V)

LFUSE_atmega8 := 0x9f
HFUSE_atmega8 := 0xca

LFUSE_atmega8535 := 0xff
HFUSE_atmega8535 := 0xc9

check_prog:
	$(AVRDUDE) $(AVRDUDE_ISP_FLAGS) -U signature:r:sig.txt:h
	@echo -n " device signature: "
	@cat sig.txt
	@rm -f sig.txt

prog: $(OUTPUT).hex size
	@echo "  --- programming flash ---"
	$(AVRDUDE) $(AVRDUDE_ISP_FLAGS) $(AVRDUDE_WRITE_FLASH)

read_fuse:
	$(AVRDUDE) $(AVRDUDE_ISP_FLAGS) -U lfuse:r:lfuse.txt:h -U hfuse:r:hfuse.txt:h
	@echo -n " lfuse: "
	@cat lfuse.txt
	@echo -n " hfuse: "
	@cat hfuse.txt
	@rm -f lfuse.txt hfuse.txt

prog_fuse:
	$(AVRDUDE) $(AVRDUDE_ISP_FLAGS) $(AVRDUDE_WRITE_FUSE)

# lock bits:
#        Bit                              Unlocked  Lock
#         7     -                             1      0
#         6     -                             1      0
# BLB12   5     Bootloader Own Section        1      0     Protect Bootloader
# BLB11   4                                   1      0
# BLB02   3     Bootloader App Section        1      1
# BLB01   2                                   1      1
# LB2     1     Memory Lock Bits              1      1
# LB1     0                                   1      1
#                                         = 0xff   = 0x0f

read_lock:
	$(AVRDUDE) $(AVRDUDE_ISP_FLAGS) -U lock:r:lock.txt:h
	@echo -n " lock byte: "
	@cat lock.txt
	@rm -f lock.txt

prog_unlock:
	$(AVRDUDE) $(AVRDUDE_ISP_FLAGS) -U lock:w:0xff:m

prog_lock:
	$(AVRDUDE) $(AVRDUDE_ISP_FLAGS) -U lock:w:0x0f:m

# program a dist hex file with the bootloader
prog_ldr:
	$(AVRDUDE) $(AVRDUDE_LDR_FLAGS) $(AVRDUDE_WRITE_FLASH)

prog_cvm8board:
	$(MAKE) prog_ldr BOARD=cvm8board BUILD=flash

prog_arduino2009:
	$(MAKE) prog_ldr BOARD=arduino2009 BUILD=flash

# ----- Bootloader ------

# boot loader address: 0xe00 -> *2 -> 0x1c00
BOOTLOADER_ADDRESS = 1C00
BOOTLOADER_LDFLAGS =  -Wl,-Map=BUILD/stk500boot.map,--cref -lm -Wl,--section-start=.text=$(BOOTLOADER_ADDRESS) -nostartfiles -nodefaultlibs
BOOTLOADER_CFLAGS = -Os -funsigned-char -funsigned-bitfields -fpack-struct -fshort-enums -mno-tablejump -Wall -Wstrict-prototypes -std=gnu99

bootloader: BUILD/stk500boot.hex

BUILD/stk500boot.elf: BUILD/stk500boot.o
	$(HIDE)$(CC) $(CFLAGS) $(BOOTLOADER_CFLAGS) $< --output $@ $(BOOTLOADER_LDFLAGS)

stk500boot.c: stk500boot.h

BUILD/stk500boot.o: stk500boot.c
	$(HIDE)$(CC) -DF_CPU=$(F_CPU) -DBAUDRATE=$(AVRDUDE_BOOTLOADER_SPEED) $(CFLAGS) $(BOOTLOADER_CFLAGS) -c -o $@ $<

clean_bootloader:
	rm -f BUILD/stk500boot.*

prog_bootloader: BUILD/stk500boot.hex
	make prog OUTPUT=BUILD/stk500boot

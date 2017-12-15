README.txt

        dtv2ser - a serial bridge device for the dtvtrans protocol

            written by Christian Vogelgsang <chris@vogelgsang.org>
            under the GNU Public License V2
            
            Homepage: http://www.lallafa.de/blog

Abstract
--------

dtvtrans is a data transfer tool and a PC parallel port cable that allows to
directly read or write memory from a DTV (a.k.a. C64 in a Joystick) via its
joystick or userport. dtvtrans is developed by Daniel Kahlin/TLR and
available here:

  http://www.kahlin.net/daniel/dtv/cable.php

dtv2ser is a small hardware device that implements the dtvtrans protocol on an
Atmel ATmega8 microcontroller. The transferred data is then passed through a
RS232 high speed serial link to a connected client computer. With this device
all PCs with RS232 can use the dtvtrans protocol. With a serial-to-USB adapter
the dtv2ser device can be connected to almost all modern hardware. The new
dtv2usb device directly combines the serial-to-USB adapter and is realized
on a small USB stick like board.

The data flow is as follows:

 DTV  <--[dtvtrans]-->  dtv2ser  <--[RS232]--> serial-to-usb <--[USB]--> client PC
                        +--------------------v-------------+
                                          dtv2usb

Features
--------
 
The dtv2ser package currently consists of the following parts:

 1.) Hardware
  - 0.2: a new schematic for an ATmega8 based board with included USB serial 
    converter using a FT 232 RL chip: dtv2usb
  - 0.2: ready-made board layout for a dtv2usb "stick-like" SMD board
  - a schematic for a minimal ATmega8 board: dtv2ser with MAX232A based 
    RS232 connection
  - both boards running at 14.54760 MHz
  - 3 LEDs for Status: "Ready" (green), "Transmit" (yellow), "Error" (red)
  - wiring for the dtvtrans DB-9 connector
  - on board 10 pin ISP connector that is also used for the bootloader jumper,
    an optional reset switch and optional external power supply.
  - dtv2usb: on board 3 pin power selector: either from USB or external
  - 0.5: added Arduino 2009 board support.
  --> see hardware/ directory
 
 2.) dtv2ser Server Firmware
  - implements all dtvtrans commands
  - a full featured firmware with rich command set
  - full description of the dtv2ser serial protocol (see doc/dtv2ser-proto.txt)
  - high speed UART serial transfer up to 230.4 kbps
  - hardware RTS/CTS handshaking, 8 bit data, parity none, 1 stop bit
  - config parameters settable during runtime and storable in EEPROM
  - added a bootloader to update the firmware directly via serial without ISP
  --> see server/ directory
 
 3.) dtv2sertrans Client Tool
  - dtv2sertrans command line tool (similar to original dtvtrans tool)
  - python module for dtv2ser communication
  - portable: runs on Mac, Linux and Windows
  - requires PySerial (http://pyserial.sourceforge.net/)
  --> see client/ directory

 NOTE: for Linux Users with dtv2ser+usb Hardware:
  the linux kernel driver for the FT232RL device is broken in some
  kernel releases! with those dtv2sertrans won't work!
  tested ok:    2.6.18
  tested ERROR: 2.6.22
  tested ok:    2.6.24

More Documentation
------------------

In the "docs" directory you will find more documentation on this project.

Here is a summary:

  dtv2ser-setup.txt         Setup your dtv2ser device and the dtv2sertrans
                            client command
                            
  dtv2ser-examples.txt      Usage examples of the dtv2sertrans command tool
  
  dtv2ser-joystick.txt      The new joystick, auto type and bootstrap
                            features added in version 0.3
  
  dtv2ser-proto.txt         A detailed description of the low level dtv2ser
                            protocol used by the host PC to communicate with
                            the dtv2ser device.

  avr-toolchain.txt         The commands I used to build a cross compiler
                            toolchain used to compile the server firmware.

Hardware Documents (located in the "hardware" directory):

  dtv2ser.pdf/.png          Schematics of the dtv2ser board
  dtv2ser.sch               Eagle schematic of dtv2ser board
  
  dtv2usb-sch.pdf/.png      Schematics of the dtv2ser+usb board
  dtv2usb-sch.sch           Eagle schematic of dtv2ser+usb board
 
  dtv2usb-manual.txt        Usage instructions for the dtv2ser+usb device
  dtv2usb-parts.txt         Parts list for the dtv2ser+usb device

  dtv2ser-arduino.txt       Instructions for Arduino 2009 HW setup

Have Fun,
-chris/lallafa
2.3.2008

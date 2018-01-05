DTV2ser ARM port
================

By James Churchill <pelrun@gmail.com> 5.12.2018

Intro
=====

As the AVR based boards in my collection didn't work well with DTV2ser - it
doesn't like the CH340 usb-serial chip - I decided to port it over to the cheap
ARM-based Blue Pill ($2 on ebay!) that does all the USB inside the ARM chip.

It's cheap, it's powerful, it's simple!

Initial programming can be done with an equally cheap ST-Link clone from ebay,
or a basic USB-serial cable.

Hardware needed
===============

STM32 Blue Pill (search for "STM32F103 minimum board" on ebay)
USB-Serial cable
(or any STM32 programmer if you have it, like a ST-Link, Discovery board,
J-Link or Black Magic Probe)

Wiring pinout
=============

The default pinout uses the 5 pins closest to the USB socket, on the side that
doesn't start with ground.

ARM   Direction   DB9
----+-----------+----
B12   Up          1
B13   Down        2
B14   Left        3
B15   Right       4
A8    Fire        6
A9    Reset       9

G     Ground      6

Building
========

Install arm-none-eabi-gcc

cd arm
make

Flash build/dtv2ser-arm.hex to the bluepill

Flashing
========
TODO: There are instructions online for flashing a bootloader on the blue pill,
just use the dtv2ser-arm.hex file instead. Presently flashing via the bluepill
USB port is not supported.

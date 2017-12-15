/*
 * ctboard.h - c't board hardware access
 *
 * Written by
 *  Christian Vogelgsang <chris@vogelgsang.org>
 *
 * This file is part of dtv2ser.
 * See README for copyright notice.
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 *  02111-1307  USA.
 *
 */

#ifndef CTBOARD_H
#define CTBOARD_H

/*
    Port A
	0		<- ANALOG+AMP		(Connector P6)		CT_TEMP0
	1		<- ANALOG+AMP		(Connector P7)		CT_TEMP1
	2		IO8					(Connector P9)		CT_LDR/NTC
	3		IO9					(Connector P10)
	4		IO10	BEEPER							CT_BEEPER
	5		IO11				(A Board?)
	6		IO12				(A Board?)
	7		IO13	XP_CP2/DTR						CT_XP_CP2

	Port B                      uC-COM         XPort-COM          uC-XPort
	0     +                       1          sniff:1=COM,0=XP          0
	1     |-SerialDirection       1               0                    x(1)
	2     +                       x               0                    1
	3		IO14	XP_CP1/RTS	(COM/CTS wenn PB1==0)
	4		IO15				(COM/CTS wenn PB1==1)
	5		MOSI	+ SPI
	6		MISO	+ SPI
	7		SCLK	+ SPI

	Port C
	0		IO0		LCD_DS
	1		IO1		LCD_SHCP
	2		IO2		LCD_STCP
	3		IO3		LCD_BUSY
	4		IO4					(Connector P10)
	5		IO5					(Connector P10)
	6		IO6					(Connector P10)
	7		IO7					(Connector P10)

	Port D
	0		MCU_RXD	+ MCU UART
	1		MCU_TXD	+ MCU UART
	2		IO16	COM_RTS		(XP_CP3 wenn PB2==0)
	3		TL0  	KEY & LED RED
	4		TL1		KEY & LED ORANGE
	5		TL2		KEY & LED YELLOW
	6		TL3		KEY & LED GREEN
	7		IO17				(XP_CP3/CTS wenn PB2==1)
*/

// ---------- DELAY ---------------------------------------------------------
#ifdef CT_BOARD_DELAY
#define CT_DELAY_100MS	5
#define CT_DELAY_500MS  25
#define CT_DELAY_1SEC   50
void ct_delay(u08 num);
#endif

// ---------- KEYS & LEDS ---------------------------------------------------
#define CT_LED_GREEN	0x40
#define CT_LED_YELLOW   0x20
#define CT_LED_ORANGE   0x10
#define CT_LED_RED      0x08
#define CT_LED_ALL      0x78

void ct_init_keyled(void);
void ct_led_on(u08 led_mask);
void ct_led_off(u08 led_mask);
//void ct_led_bits(u08 num);
#ifdef CT_BOARD_KEYS
u08 ct_get_key_press(void);
#endif

// ---------- BEEPER --------------------------------------------------------
#ifdef USE_BEEPER
void ct_init_beeper(void);
void ct_beep(u08 ms);
#endif

// ---------- UART MPLEX ----------------------------------------------------
// COPY_... defines what is transferred to XPT
#define CT_MPLEX_COM_MCU_COPY_COM		0x03
#define CT_MPLEX_COM_MCU_COPY_MCU		0x07
// COPY_... defines what is transferred to MCU
#define CT_MPLEX_COM_XPT_COPY_COM		0x01
#define CT_MPLEX_COM_XPT_COPY_XPT		0x00
// COPY_... defines what is transferred to COM
#define CT_MPLEX_MCU_XPT_COPY_MCU       0x06
#define CT_MPLEX_MCU_XPT_COPY_XPT		0x04
// invalid mplex modes
#define CT_MPLEX_INVALID1				0x02
#define CT_MPLEX_INVALID2				0x05
// bitmask for all mplex bits
#define CT_MPLEX_MASK					0x07
void ct_init_mplex(void);
void ct_set_mplex(u08 mode);

// ---------- LCD -----------------------------------------------------------
#ifdef USE_LCD

#define CT_LCD_MODE_OFF         0x08
#define CT_LCD_MODE_ON          0x0c
#define CT_LCD_MODE_ON_CURSOR   0x0e
#define CT_LCD_MODE_ON_BLINK    0x0f

#define CT_LCD_CMD_CLEAR        0x01
#define CT_LCD_CMD_INIT         0x38
#define CT_LCD_CMD_ADDR         0x80

#define CT_LCD_RS_BIT           0x01
#define CT_LCD_RW_BIT           0x02
#define CT_LCD_E_BIT            0x04
#define CT_LCD_D_BIT            0x08

void ct_lcd_init(void);
void ct_lcd_u08(u08 cmd, u08 cmdOrData);
void ct_lcd_pos(u08 x,u08 y);
//void ct_lcd_mode(u08 mode);
//void ct_lcd_line(u08 y,u08 *line,u08 len);
//void ct_lcd_string(u08 *str);

#define ct_lcd_data(a)        ct_lcd_u08(a, CT_LCD_RS_BIT)
#define ct_lcd_cmd(a)         ct_lcd_u08(a, 0)

#define ct_lcd_clear()        ct_lcd_cmd(CT_LCD_CMD_CLEAR)
#define ct_lcd_char(b)        ct_lcd_data(b)

#endif

// ---------- ADC -----------------------------------------------------------
#ifdef CT_BOARD_ADC
u16 ct_read_adc(u08 channel);
#endif

// ---------- GPIO ----------------------------------------------------------
#ifdef CT_BOARD_GPIO
#define CP_DEF(NUM) \
void ct_set_cp ## NUM ## _dir(u08 out); \
u08 ct_get_cp ## NUM ## _dir(void); \
void ct_set_cp ## NUM (u08 on); \
u08 ct_get_cp ## NUM (void);
CP_DEF(1)
CP_DEF(2)
CP_DEF(3)
#endif

// ---------- RTS/CTS -------------------------------------------------------
#ifdef USE_XPORT
void ct_xport_init_rts_cts(void);
u08 ct_xport_get_rts(void);
void ct_xport_set_cts(u08 on);
#else
void ct_com_init_rts_cts(void);
u08 ct_com_get_rts(void);
void ct_com_set_cts(u08 on);
#endif

#endif

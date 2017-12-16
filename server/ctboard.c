/*
 * ctboard.c - c't board hardware access
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

#include "global.h"

#include <avr/io.h>
#include <util/delay.h>

#include "ctboard.h"

// ---------- DELAY ---------------------------------------------------------

#ifdef CT_BOARD_DELAY

void ct_delay(uint8_t num)
{
  uint8_t counter;
  for(counter=0;counter<num;counter++) {
    _delay_loop_2(30000);
    counter++;
  }
}

#endif

// ---------- KEYS & LEDS ---------------------------------------------------

#ifdef CT_BOARD_KEYS
static uint8_t key_state;
#endif

void ct_init_keyled(void)
{
  DDRD |= CT_LED_ALL;	// led output
  PORTD |= CT_LED_ALL;
#ifdef CT_BOARD_KEYS
  key_state = 0;
#endif
}

void ct_led_on(uint8_t led_mask)
{
  PORTD &= ~led_mask;
}

void ct_led_off(uint8_t led_mask)
{
  PORTD |= led_mask;
}

#if 0
void ct_led_bits(uint8_t bits)
{
  bits = (~bits & 0xf) << 3;
  PORTD &= ~ CT_LED_ALL;
  PORTD |= bits;
}
#endif

#ifdef CT_BOARD_KEYS

uint8_t ct_read_keys(void)
{
  // read old led state
  uint8_t oldPORTD = PORTD;
  uint8_t result;

  // disable outputs of leds and activate pullups
  DDRD &= ~CT_LED_ALL;
  PORTD |= CT_LED_ALL;

  // read in key pins
  result = ~PIND & CT_LED_ALL;

  // restore output led state
  DDRD |= CT_LED_ALL;
  PORTD = oldPORTD;
  return result;
}

uint8_t ct_get_key_press()
{
  uint8_t i,j,changed;

  // read initial keystate
  uint8_t new_key_state = ct_read_keys();

  // no keys pressed -> return 0
  if(new_key_state == 0) {
    key_state = 0;
    return 0;
  }

  // nothing has changed
  if(new_key_state == key_state) {
    return 0;
  }

  // make sure state is stable
  for(i=0;i<10;i++) {
    uint8_t temp_key_state = ct_read_keys();
    if(temp_key_state != new_key_state)
      return 0;
    for(j=0;j<255;j++) { asm("nop"); }
  }

  // save key state and return changed keys
  new_key_state = ct_read_keys();
  changed = key_state ^ new_key_state;
  key_state = new_key_state;
  return changed;
}

#endif

// ---------- BEEPER --------------------------------------------------------

#ifdef USE_BEEPER

void ct_init_beeper(void)
{
  DDRA|=0x10; // PA4 (beeper) is output
}


static void ct_beep_toggle(void)
{
  PORTA = PORTA ^ 0x10;
}

void ct_beep(uint8_t num)
{
  uint8_t i;
  for(i=0;i<num;i++) {
    uint8_t j;
    for(j=0;j<100;j++) {
      ct_beep_toggle();
      _delay_loop_2(1000);
    }
    for(j=0;j<100;j++) {
      _delay_loop_2(1000);
    }
  }
}

#endif

// ---------- MPLEX ---------------------------------------------------------

void ct_init_mplex(void)
{
	DDRB|= 0x07; // PB0-PB2 is output
	PORTB &= ~CT_MPLEX_MASK;
	PORTB |= CT_MPLEX_MCU_XPT_COPY_XPT;
}

void ct_set_mplex(uint8_t mode)
{
	uint8_t pb = PORTB & ~CT_MPLEX_MASK;
	PORTB = pb | mode;
}

// ---------- RTS/CTS -------------------------------------------------------

#ifdef USE_XPORT

void ct_xport_init_rts_cts(void)
{
  DDRB  &=  ~0x08; // PB3 is input from XPort/GP1/RTS/output
  PORTB |=   0x08;

  DDRD  |=   0x80; // PD7 is output to XPort/GP3/CTS/input
  PORTD &=  ~0x80; // low active: allow sending from XPort
}

uint8_t ct_xport_get_rts(void)
{
  return (PINB & 0x08) == 0x08;
}

void ct_xport_set_cts(uint8_t on)
{
  if(on)
    PORTD &= ~0x80; // low active: allow sending from XPort
  else
    PORTD |=  0x80; // deny sending from XPort
}

#else

void ct_com_init_rts_cts(void)
{
  DDRD  &=  ~0x04; // PD2 is input from COM/RTS
  PORTD |=   0x04;

  DDRB  |=   0x10; // PB4 is output to COM/CTS
  PORTB &=  ~0x10; // low active!
}

uint8_t ct_com_get_rts(void)
{
  return (PIND & 0x04) == 0x00;
}

void ct_com_set_cts(uint8_t on)
{
  if(on)
    PORTB &= ~0x10; // low active: allow sending from XPort
  else
    PORTB |=  0x10; // deny sending from XPort
}

#endif

// ---------- LCD -----------------------------------------------------------

#ifdef USE_LCD

#define LCD_NOP      asm("nop")

#define DISPLAY_PINS 0x0F
#define DPC        (PORTC & ~DISPLAY_PINS)
#define DRC        (DDRC & ~DISPLAY_PINS)
#define DPC_C(c)   ((PORTC & (~DISPLAY_PINS|~c))) /* c-bit(s) loeschen */
#define DPC_T(s,c) ((PORTC & (~DISPLAY_PINS|~c))|(s & DISPLAY_PINS)) /* s-bit(s) setzen, c-bit(s) loeschen */

static void ct_lcd_wait_busy(void)
{
  uint8_t data = CT_LCD_D_BIT;
  LCD_NOP;
  while (data) { // 67.8ns
    PORTC = DPC_T(CT_LCD_RW_BIT,(CT_LCD_RW_BIT|CT_LCD_E_BIT)); // RS=0, RW=1, E=0  // dauer ca. 4 takte
    // Wait tAS (140ns min). bei 14.7456MHz < 3 takte von etwa 67.8ns
    LCD_NOP;         // - Port lesen - Port AND + ODER
    PORTC = DPC_T((CT_LCD_RW_BIT|CT_LCD_E_BIT),CT_LCD_RS_BIT);  // RS=0, RW=1, E=1 // ca. 4 takte
    // Wait tDA (450ns[tEH]-200ns[tDS]=250ns min) =~ 4 takte
    LCD_NOP;
    LCD_NOP;
    LCD_NOP;
    LCD_NOP;
    LCD_NOP;  // ein takt dazu da OUT erst einen Takt spaeter am Pin anliegt.
    data = (PINC & CT_LCD_D_BIT);  // Flag lesen
    // einlesen + verunden = 2 * 7.ns = 140 + ca. 350ns = 490ns > tEH [min=450ns]
    PORTC = DPC_C(CT_LCD_E_BIT); // E zuruecksetzen
    // tEL[min=500ns] warten falls nicht "nicht busy"
    if(data) { // busy  67.8 ns
      // bereits ca. 210 aussen rum
      LCD_NOP; // sollte reichen
      LCD_NOP;
      LCD_NOP;
      LCD_NOP;
    }
  }
  PORTC = DPC_C((CT_LCD_RS_BIT|CT_LCD_RW_BIT|CT_LCD_E_BIT)); // RS=0, RW=0, E=0
}

// 1 takt =~ 67.8ns bei 14.7456MHz
void ct_lcd_uint8_t(uint8_t cmd, uint8_t cmdOrData){
  uint8_t i;

  ct_lcd_wait_busy();

  // shift out bits
  for (i=0;i<8;i++){
    PORTC = DPC | ((cmd >> 7)&1);  // Das oberste Bit von cmd auf PC0
    // Takte schieberegister
    PORTC |= CT_LCD_RW_BIT;           // und PC1 takten
    cmd = cmd << 1;            // cmd links schieben
    PORTC = DPC;// | 0x00;
  }

  // Warte tAS[min=140ns] bevor E_BIT
  // 140ns/67.8ns =~ 2.1 < 3
  LCD_NOP;
  PORTC = DPC | (CT_LCD_E_BIT | cmdOrData); // RS=0, RW=0, E setzen, damit wird gleichzeitig Inhalt

  // des Schieberegisters auf die parallelen Displayleitungen gegeben
  // das Display ist LAHM, daher warten
  // Warte tEH[min=450ns]
  // 450ns/67.8ns <= 7
  LCD_NOP; LCD_NOP; LCD_NOP;
  LCD_NOP; LCD_NOP; LCD_NOP;
  LCD_NOP;
  PORTC = DPC | cmdOrData;
}

static const uint8_t lcd_off[4] = { 0x00,0x40,0x14,0x54 };

void ct_lcd_init(void)
{
  DDRC = DRC | 7;
  ct_lcd_cmd(CT_LCD_CMD_INIT);
  ct_lcd_cmd(CT_LCD_MODE_ON);
  ct_lcd_cmd(CT_LCD_CMD_CLEAR);
}

#if 0
void cd_lcd_mode(uint8_t mode)
{
  ct_lcd_cmd(mode);
}
#endif

#if 0
void ct_lcd_line(uint8_t y,uint8_t *line,uint8_t len)
{
  uint8_t i;

  ct_lcd_cmd(CT_LCD_CMD_ADDR + lcd_off[y]);
  for(i=0;i<len;i++)
    ct_lcd_data(line[i]);
}
#endif

void ct_lcd_pos(uint8_t x,uint8_t y)
{
  ct_lcd_cmd(CT_LCD_CMD_ADDR + lcd_off[y] + x);
}

#if 0
void ct_lcd_string(uint8_t *str)
{
  while(*str) {
    ct_lcd_data(*str);
    str++;
  }
}
#endif

#endif

// ---------- ADC -----------------------------------------------------------

#ifdef CT_BOARD_ADC

// adc readout (code by Benjamin Benz/c't magazin)
uint16_t ct_read_adc(uint8_t channel)
{
  uint8_t oldDDRA  = DDRA;
  uint8_t oldPORTA = PORTA;

  // prepare for readout
  DDRA  &= ~ (1<<channel);
  PORTA &= ~ (1<<channel);

  ADMUX = 0x80+0x40;
  ADMUX |= channel;

  // prescale 64: 14,7456MHz / 64 = 230,4 kHz
  ADCSRA= (1 << ADPS2) | (1<<ADPS1) | (1 << ADEN) | (1 << ADSC);

  // wait for conversion end
  while ( (ADCSRA & (1<<ADSC)) != 0){}

  // fetch value (first ADCL then ADCH!!)
  uint8_t lo = ADCL;
  uint8_t hi = ADCH;
  uint16_t result= lo | (hi <<8);

  DDRA  = oldDDRA;
  PORTA = oldPORTA;

  return result;
}

#endif

// ---------- GPIO ----------------------------------------------------------

#ifdef CT_BOARD_GPIO

#define CP_PROC(NUM,DDR,PORT,BIT) \
void ct_set_cp ## NUM ## _dir(uint8_t out) \
{ \
  if(out) \
    DDR |=  (1<<BIT); \
  else \
    DDR &= ~(1<<BIT); \
} \
uint8_t ct_get_cp ## NUM ## _dir(void) \
{ \
  return (DDR & (1<<BIT)) == (1<<BIT); \
} \
void ct_set_cp ## NUM (uint8_t on) \
{ \
  if(on) \
    PORT |=  (1<<BIT); \
  else \
    PORT &= ~(1<<BIT); \
  } \
uint8_t ct_get_cp ## NUM (void) \
{ \
  return (PORT & (1<<BIT)) == (1<<BIT); \
}

CP_PROC(1,DDRB,PORTB,3)
CP_PROC(2,DDRA,PORTA,7)
CP_PROC(3,DDRD,PORTD,2)

#endif

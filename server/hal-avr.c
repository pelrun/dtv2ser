
#include <stdint.h>
#include <avr/io.h>
#include <util/delay.h>

#include "board.h"

void dtvlow_ack(uint8_t val)
{
  if (val)
  {
    // set ack input+pullup
    DTVLOW_ACKRESET_DDR  &=  ~DTVLOW_ACK_MASK;
    DTVLOW_ACKRESET_PORT |=   DTVLOW_ACK_MASK;
  }
  else
  {
    // set ack output low
    DTVLOW_ACKRESET_DDR  |=  DTVLOW_ACK_MASK;
    DTVLOW_ACKRESET_PORT &=  ~DTVLOW_ACK_MASK;
  }
}

uint8_t dtvlow_ack_get(void)
{
  return (DTVLOW_ACKRESET_PIN & DTVLOW_ACK_MASK)?1:0;
}

void dtvlow_clk(uint8_t val)
{
  if (val)
  {
    // set clk input+pullup
    DTVLOW_DATACLK_DDR   &= ~DTVLOW_CLK_MASK;
    DTVLOW_DATACLK_PORT  |=  DTVLOW_CLK_MASK;
  }
  else
  {
    // set clk output low
    DTVLOW_DATACLK_DDR  |= DTVLOW_CLK_MASK;
    DTVLOW_DATACLK_PORT &= ~DTVLOW_CLK_MASK;
  }
}

void dtvlow_rst(uint8_t val)
{
  DTVLOW_ACKRESET_DDR |= DTVLOW_RESET_MASK;
  if (val)
  {
    DTVLOW_ACKRESET_PORT |= DTVLOW_RESET_MASK;
  }
  else
  {
    DTVLOW_ACKRESET_PORT &= ~DTVLOW_RESET_MASK;
  }
}

void dtvlow_data(uint8_t val)
{
  uint8_t out;
  uint8_t data = val&0x07 << DTVLOW_DATA_SHIFT;

  // Open-drain emulation: set output for low bits
  // and input for high bits
  DTVLOW_DATACLK_DDR &= ~DTVLOW_DATA_MASK;
  DTVLOW_DATACLK_DDR |= (~data) & DTVLOW_DATA_MASK;

  out = DTVLOW_DATACLK_PORT;
  out &= ~DTVLOW_DATA_MASK;
  out |= data;
  DTVLOW_DATACLK_PORT = out;
}

uint8_t dtvlow_data_get(void)
{
  return (DTVLOW_DATACLK_PIN & DTVLOW_DATA_MASK) >> DTVLOW_DATA_SHIFT;
}

void dtvlow_recv_delay(uint8_t delay)
{
  _delay_loop_1(delay);
}

#ifdef USE_JOYSTICK

void joy_begin(void)
{
  JOY_PORT |= JOY_MASK;
  JOY_DDR  |= JOY_MASK;
}

void joy_out(uint8_t value)
{
  JOY_PORT = (~value & JOY_MASK) | ~(JOY_MASK);
}

void joy_end(void)
{
  JOY_PORT |=   JOY_MASK;
  JOY_DDR  &= ~(JOY_MASK);
}

#endif

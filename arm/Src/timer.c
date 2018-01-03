
#include <stdint.h>

#include <stm32f1xx_hal.h>

#include "board.h"

#include "timer.h"

void timer_init(void)
{
}

void timer_delay_1ms(uint16_t timeout)
{ 
  uint16_t start = timer_now();
  while((uint16_t)(timer_now()-start)<timeout);
}

uint8_t timer_expired(timeout_t *t)
{
  return (uint16_t)(timer_now() - t->start) > t->timeout;
}

uint16_t timer_now(void)
{
  return HAL_GetTick() & 0xffff;
}

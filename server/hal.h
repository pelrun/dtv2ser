
#ifndef _HAL_H
#define _HAL_H

void dtvlow_ack(uint8_t val);

uint8_t dtvlow_ack_get(void);

void dtvlow_clk(uint8_t val);

void dtvlow_rst(uint8_t val);

void dtvlow_data(uint8_t val);

uint8_t dtvlow_data_get(void);

void dtvlow_recv_delay(uint8_t delay);

#endif // _HAL_H

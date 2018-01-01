
#ifndef _HAL_H
#define _HAL_H

void dtvlow_ack(uint8_t val);
uint8_t dtvlow_ack_get(void);

void dtvlow_clk(uint8_t val);

void dtvlow_rst(uint8_t val);

void dtvlow_data(uint8_t val);
uint8_t dtvlow_data_get(void);

void dtvlow_recv_delay(uint8_t delay);

#define JOY_MASK        0x1f

#define JOY_MASK_UP     0x01
#define JOY_MASK_DOWN   0x02
#define JOY_MASK_LEFT   0x04
#define JOY_MASK_RIGHT  0x08
#define JOY_MASK_FIRE   0x10

void joy_begin(void);
void joy_out(uint8_t value);
void joy_end(void);

#endif // _HAL_H

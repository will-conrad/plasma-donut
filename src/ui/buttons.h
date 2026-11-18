/* buttons.h - debounce and short/long press detection. Pure C, host-testable.
 * The caller reads the pin (active low) and passes pressed = true/false,
 * with a millisecond timestamp, every BTN_POLL_MS. */
#ifndef BUTTONS_H
#define BUTTONS_H
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    BTN_EV_NONE = 0,
    BTN_EV_SHORT,   /* released before BTN_LONG_MS */
    BTN_EV_LONG     /* fires once, as soon as the hold reaches BTN_LONG_MS */
} btn_event_t;

typedef struct {
    bool     stable;      /* debounced state: true = pressed */
    bool     last_raw;
    uint32_t t_change;    /* when last_raw last changed */
    uint32_t t_press;     /* when stable became pressed */
    bool     long_fired;
} btn_t;

void        btn_init(btn_t *b);
btn_event_t btn_update(btn_t *b, bool pressed, uint32_t now_ms);
const char *btn_event_str(btn_event_t e);

#endif

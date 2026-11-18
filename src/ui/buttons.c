#include "buttons.h"
#include "../config/config.h"

void btn_init(btn_t *b)
{
    b->stable = false;
    b->last_raw = false;
    b->t_change = 0;
    b->t_press = 0;
    b->long_fired = false;
}

btn_event_t btn_update(btn_t *b, bool pressed, uint32_t now_ms)
{
    /* Step 1: restart the debounce timer whenever the raw input moves. */
    if (pressed != b->last_raw) {
        b->last_raw = pressed;
        b->t_change = now_ms;
    }

    /* Step 2: accept the new level once it has held for BTN_DEBOUNCE_MS. */
    if (b->stable != b->last_raw && (uint32_t)(now_ms - b->t_change) >= BTN_DEBOUNCE_MS) {
        b->stable = b->last_raw;
        if (b->stable) {
            b->t_press = now_ms;
            b->long_fired = false;
        } else if (!b->long_fired) {
            return BTN_EV_SHORT;       /* released before the long-press time */
        }
    }

    /* Step 3: long press fires once while still held, so the UI reacts
     * without waiting for the release. Its release then reports nothing. */
    if (b->stable && !b->long_fired && (uint32_t)(now_ms - b->t_press) >= BTN_LONG_MS) {
        b->long_fired = true;
        return BTN_EV_LONG;
    }
    return BTN_EV_NONE;
}

const char *btn_event_str(btn_event_t e)
{
    switch (e) {
    case BTN_EV_NONE:  return "none";
    case BTN_EV_SHORT: return "short";
    case BTN_EV_LONG:  return "long";
    }
    return "?";
}

/* Host tests for the button state machine (src/ui/buttons.c). */
#include <assert.h>
#include <stdio.h>
#include "ui/buttons.h"
#include "config/config.h"

static btn_t b;
static uint32_t t;
static int n_short, n_long;

/* Feed one level for `ms` milliseconds, polling every BTN_POLL_MS. */
static void hold(bool pressed, uint32_t ms)
{
    for (uint32_t i = 0; i < ms; i += BTN_POLL_MS, t += BTN_POLL_MS) {
        btn_event_t e = btn_update(&b, pressed, t);
        if (e == BTN_EV_SHORT) n_short++;
        if (e == BTN_EV_LONG)  n_long++;
    }
}

static void reset(void) { btn_init(&b); t = 1000; n_short = n_long = 0; }

int main(void)
{
    /* clean short press */
    reset(); hold(false, 100); hold(true, 200); hold(false, 100);
    assert(n_short == 1 && n_long == 0);

    /* contact bounce on press and release still gives one short press */
    reset(); hold(false, 50);
    hold(true, 10); hold(false, 10); hold(true, 10); hold(false, 10);
    hold(true, 300);
    hold(false, 10); hold(true, 10); hold(false, 100);
    assert(n_short == 1 && n_long == 0);

    /* a 10 ms glitch is shorter than the debounce time: ignored */
    reset(); hold(false, 50); hold(true, 10); hold(false, 200);
    assert(n_short == 0 && n_long == 0);

    /* long press fires once while held; its release adds nothing */
    reset(); hold(false, 50); hold(true, 2000);
    assert(n_long == 1 && n_short == 0);
    hold(false, 100);
    assert(n_long == 1 && n_short == 0);

    /* just under the long threshold is still short */
    reset(); hold(false, 50); hold(true, BTN_LONG_MS - 50); hold(false, 100);
    assert(n_short == 1 && n_long == 0);

    /* two presses in a row */
    reset(); hold(true, 100); hold(false, 100); hold(true, 100); hold(false, 100);
    assert(n_short == 2);

    /* millisecond counter wrapping past 2^32 does not break timing */
    btn_init(&b); t = 0xFFFFFF00u; n_short = n_long = 0;
    hold(false, 50); hold(true, 1000);
    assert(n_long == 1);

    printf("test_buttons: all passed\n");
    return 0;
}

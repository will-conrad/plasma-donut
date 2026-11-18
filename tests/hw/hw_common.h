/* hw_common.h - shared start-up for the bring-up test programs. */
#ifndef HW_COMMON_H
#define HW_COMMON_H
#include <stdio.h>
#include "pico/stdlib.h"

/* Start USB serial and wait up to 5 s for the Mac to open the port, so the
 * first lines are not lost. Runs on regardless after that. */
static inline void hw_start(const char *title)
{
    stdio_init_all();
    for (int i = 0; i < 50 && !stdio_usb_connected(); i++) sleep_ms(100);
    printf("\n=== %s ===\n", title);
}

#endif

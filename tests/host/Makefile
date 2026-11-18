# Host tests: pure C, no Pico needed.   make -C tests/host
CC     ?= cc
CFLAGS  = -std=c11 -Wall -Wextra -Werror -I../../src
OUT     = ../../build/host

test: $(OUT)/test_convert $(OUT)/test_mcp3208_frame $(OUT)/test_gfx $(OUT)/test_buttons
	@for t in $^; do $$t || exit 1; done

$(OUT)/test_convert: test_convert.c ../../src/sensors/convert.c
	@mkdir -p $(OUT) && $(CC) $(CFLAGS) $^ -lm -o $@
$(OUT)/test_mcp3208_frame: test_mcp3208_frame.c
	@mkdir -p $(OUT) && $(CC) $(CFLAGS) $^ -o $@
$(OUT)/test_gfx: test_gfx.c ../../src/ui/gfx.c
	@mkdir -p $(OUT) && $(CC) $(CFLAGS) $^ -o $@

$(OUT)/test_buttons: test_buttons.c ../../src/ui/buttons.c
	@mkdir -p $(OUT) && $(CC) $(CFLAGS) $^ -o $@

.PHONY: test

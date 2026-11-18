# Plasma Donut control-board firmware (Pico 2 / RP2350, Pico SDK 2.3.1)
#   export PICO_SDK_PATH=~/pico/pico-sdk
#   cmake -B build -DPICO_BOARD=pico2 && cmake --build build
cmake_minimum_required(VERSION 3.13)

if(NOT DEFINED PICO_BOARD)
    set(PICO_BOARD pico2)
endif()

include(pico_sdk_import.cmake)          # must come before project()
project(plasma_donut C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()

set(DONUT_SENSORS src/sensors/convert.c)
set(DONUT_MCP     src/drivers/mcp3208.c)
set(DONUT_PICOADC src/drivers/picoadc.c)
set(DONUT_LCD     src/drivers/st7565.c src/ui/gfx.c src/ui/backlight.c)
set(DONUT_BUTTONS src/ui/buttons.c)

# One UF2 per bring-up step: add_hw_test(<name> <sources...>)
function(add_hw_test name)
    add_executable(${name} tests/hw/${name}.c ${ARGN})
    target_include_directories(${name} PRIVATE src)
    target_compile_options(${name} PRIVATE -Wall -Wextra)
    target_link_libraries(${name} pico_stdlib hardware_spi hardware_adc hardware_pwm hardware_clocks)
    pico_enable_stdio_usb(${name} 1)
    pico_enable_stdio_uart(${name} 0)
    pico_add_extra_outputs(${name})     # makes the .uf2
endfunction()

add_hw_test(step1_pico     ${DONUT_PICOADC} ${DONUT_SENSORS})
add_hw_test(step2_buttons  ${DONUT_LCD} ${DONUT_BUTTONS})
add_hw_test(step3_lcd      ${DONUT_LCD})
add_hw_test(step4_backlight ${DONUT_LCD} ${DONUT_BUTTONS})
add_hw_test(step5_mcp3208  ${DONUT_MCP} ${DONUT_SENSORS})
add_hw_test(step6a_picoadc ${DONUT_PICOADC} ${DONUT_SENSORS})
add_hw_test(step6b_temps   ${DONUT_MCP} ${DONUT_SENSORS})

# Display demo, not part of the bring-up order: plays frames from tools/stream_frames.py
add_hw_test(adc_live ${DONUT_MCP} ${DONUT_PICOADC} ${DONUT_SENSORS} ${DONUT_LCD} ${DONUT_BUTTONS})
add_hw_test(demo_frames ${DONUT_LCD})

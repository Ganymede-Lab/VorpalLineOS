# Desktop Agent Handoff

## Current Project State & Recent Wins
- **Build System Upgraded:** We successfully refactored the project to compile `.mpy` bytecode using `build_shard.py` and `compile_shards.py`. All raw code lives in `src/`, and the final flashable payload is generated in `deploy/`.
- **ESP32-S2 Hardware Support Fixed:** 
  - Fixed a critical crash where `cyberdeck_bridge.py` hardcoded `UART(2)`. The S2 only has UART0 and UART1. We abstracted the UART interfaces into `CYBERDECK_UART_ID` across the board definitions in `src/hal/boards/`.
  - Added a `time.sleep(1.5)` at the top of `main.py` to allow the S2's Native USB CDC stack to reconnect to the host before it prints the boot sequence.
- **MicroPython & Thonny IDE Gotchas:** Documented in `README.md` that users *must* wipe stale `.py` files from the ESP32 before uploading `.mpy` files. We also identified that Thonny's "Stop" button intercepts `main.py` execution on boot, requiring a physical board reset to trigger a true OS boot.

## Current Hardware Architecture
- **Host Shard:** ESP32 WROOM (Dual-core, BT support). The user is currently wiring this to an Arduino Uno Q.
- **Peripheral Shard:** Adafruit Metro ESP32-S2 (Native USB, extra GPIOs). Connected to the Host Shard via the Cyberdeck UART Bridge.
- **Future Host Architecture:** The user plans to eventually upgrade the master Host to a **Portenta X8** and Portenta Max Carrier (running full Linux and native ROS 2).

## Next Immediate Steps
1. The user is currently finishing the physical wiring between the ESP32 WROOM, the ESP32-S2, and the Arduino Uno.
2. The next major coding task is to develop the **ROS 2 message handling logic** inside `src/core/roles/ros2_shard.py`. We need to define how the ESP32 parses, translates, and routes standard micro-ROS/JSON commands over its bridges. 
3. After the ROS 2 logic is built out, we will need to implement the UART pinging logic on the Host Shard to establish communication with the peripheral shards.

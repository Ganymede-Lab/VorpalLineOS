# VorpaLine OS

VorpaLine OS is a highly optimized, MicroPython-based operating system designed for ESP32 microcontrollers. It features a non-blocking state machine, dynamic module loading, and high-speed hardware access for use as a peripheral "shard" in a larger Cyberdeck or multi-node architecture.

## Key Features

* **Non-Blocking Architecture:** The core (`VorpaLineOS`) utilizes a continuous state machine (`STATE_BOOTING`, `STATE_INIT_HAL`, `STATE_OFFLINE_STANDBY`) that avoids blocking the CPU, allowing for continuous polling and background tasks without locking up the system.
* **Cyberdeck Bridge:** A zero-allocation, non-blocking UART bridge (`hal.cyberdeck_bridge`) operating on UART2 (Pins 16 & 17) allows JSON-based command execution (like `ls`, `read`, `write`, `rm`) from a host device.
* **Viper-Optimized HAL:** Uses `@micropython.viper` for memory-mapped register access (`hal.pin_map`), allowing for single-cycle, sub-microsecond GPIO toggling that completely bypasses the standard MicroPython `machine.Pin` overhead.
* **Dynamic Loading:** Modules are loaded on-the-fly based on the `shard_profile.json` configuration, maximizing available heap memory.
* **Automated Bytecode Compilation:** Includes `compile_shards.py` to cross-compile human-readable `.py` files into memory-efficient `.mpy` bytecode.

## Installation & Deployment

1. **Compile Bytecode:** Run the included `compile_shards.py` script on your host machine to generate `.mpy` files for all core and HAL modules.
   ```bash
   python compile_shards.py
   ```
2. **Upload to ESP32:** Upload `boot.py`, `main.py`, `shard_profile.json`, and the generated `.mpy` files to the root directory of your ESP32. (Do **not** upload the raw `.py` files for `core/` and `hal/` to save flash and RAM).
3. **Hardware Wiring:** Connect your host device to the ESP32's UART2 pins:
   * **ESP32 TX:** GPIO 17
   * **ESP32 RX:** GPIO 16
   * **GND:** Must share a common ground with the host.
   * *Note: If your host device (e.g., standard Arduino Uno) uses 5V logic, you MUST use a logic level converter or a voltage divider on the line connecting the Host TX to the ESP32 RX to avoid damaging the 3.3V ESP32.*

## Configuration
The `shard_profile.json` file controls the shard's identity and active modules.
```json
{
  "shard_id": "SHARD_001",
  "role_class": "HostShard",
  "board_type": "esp32-wroom",
  "active_modules": [
    "sys", 
    "machine",
    "hal.cyberdeck_bridge"
  ]
}
```

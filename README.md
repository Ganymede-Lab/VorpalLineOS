# VorpaLine OS

VorpaLine OS is a highly optimized, MicroPython-based operating system designed for ESP32 microcontrollers. It features a non-blocking state machine, dynamic module loading, and high-speed hardware access for use as a peripheral "shard" in a larger Cyberdeck or multi-node architecture.

## Key Features

* **Non-Blocking Architecture:** The core (`VorpaLineOS`) utilizes a continuous state machine (`STATE_BOOTING`, `STATE_INIT_HAL`, `STATE_OFFLINE_STANDBY`) that avoids blocking the CPU, allowing for continuous polling and background tasks without locking up the system.
* **Cyberdeck Bridge:** A zero-allocation, non-blocking UART bridge (`hal.cyberdeck_bridge`) operating on UART2 (Pins 16 & 17) allows JSON-based command execution (like `ls`, `read`, `write`, `rm`) from a host device.
* **Viper-Optimized HAL:** Uses `@micropython.viper` for memory-mapped register access (`hal.pin_map`), allowing for single-cycle, sub-microsecond GPIO toggling that completely bypasses the standard MicroPython `machine.Pin` overhead.
* **Dynamic Loading:** Modules are loaded on-the-fly based on the `shard_profile.json` configuration, maximizing available heap memory.
* **Automated Bytecode Compilation:** Includes `compile_shards.py` to cross-compile human-readable `.py` files into memory-efficient `.mpy` bytecode.

## Installation & Deployment

1. **Build and Configure:** Run the `build_shard.py` script to select a profile (e.g., Host Shard or ROS 2 Shard) and a board. This will automatically cross-compile the code and stage the final firmware in the `deploy/` directory.
   ```bash
   python3 build_shard.py
   ```
2. **Upload to ESP32:** Simply upload the entire contents of the generated `deploy/` directory to the root of your ESP32. (It contains everything needed: `boot.py`, `main.py`, the configuration, and all the compiled `.mpy` files).
3. **Hardware Wiring:** Connect your host device to the ESP32:
   * **Cyberdeck Bridge (UART2):** TX (GPIO 17), RX (GPIO 16)
   * **ROS 2 USB Bridge:** Standard USB data pins
   * *Note: Ensure common ground and appropriate voltage logic levels (3.3V).*

## Configuration

Profiles are stored in the `profiles/` directory. The `build_shard.py` tool sets the active profile as `shard_profile.json` in the root. 

Example (`ros2_shard.json`):
```json
{
  "shard_id": "ROS2_BRIDGE_001",
  "role_class": "core.roles.ros2_shard.Ros2Shard",
  "board_type": "esp32-wroom",
  "active_modules": [
    "sys", 
    "machine",
    "hal.usb_bridge"
  ]
}
```

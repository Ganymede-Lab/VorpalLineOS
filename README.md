# VorpaLine OS

VorpaLine OS is a highly optimized, MicroPython-based operating system designed for ESP32 microcontrollers. It features a non-blocking state machine, dynamic module loading, and high-speed hardware access for use as a peripheral "shard" in a larger Cyberdeck or multi-node architecture.

## Key Features

* **Non-Blocking Architecture:** The core (`VorpaLineOS`) utilizes a continuous state machine (`STATE_BOOTING`, `STATE_INIT_HAL`, `STATE_OFFLINE_STANDBY`) that avoids blocking the CPU, allowing for continuous polling and background tasks without locking up the system.
* **Cyberdeck Bridge:** A zero-allocation, non-blocking UART bridge (`hal.cyberdeck_bridge`) allows JSON-based command execution from a host device. UART interfaces are dynamically mapped based on your board's hardware capabilities.
* **Viper-Optimized HAL:** Uses `@micropython.viper` for memory-mapped register access (`hal.pin_map`), allowing for single-cycle, sub-microsecond GPIO toggling that completely bypasses the standard MicroPython `machine.Pin` overhead.
* **Dynamic Loading:** Modules are loaded on-the-fly based on the `shard_profile.json` configuration, maximizing available heap memory.
* **Automated Bytecode Compilation:** Includes `build_shard.py` and `compile_shards.py` to cross-compile human-readable `.py` source code into memory-efficient `.mpy` bytecode, staging it cleanly in a `deploy/` directory.

## Installation & Deployment

VorpaLine OS utilizes a strict separation between source code (`src/`) and the final compiled payload (`deploy/`).

1. **Build and Configure:** Run the `build_shard.py` script to select your hardware board (e.g., Adafruit Metro ESP32-S2 or standard WROOM) and your desired shard profile. This will automatically cross-compile the code and stage the final firmware in the `deploy/` directory.
   ```bash
   python3 build_shard.py
   ```

2. **Wipe Stale Files:** Before uploading, **you must delete all `.py` files inside the `hal/` and `core/` directories on your ESP32**. MicroPython prefers raw `.py` files over compiled `.mpy` files. If you leave old raw code on the board, it will secretly import the stale code instead of your newly compiled binaries!

3. **Upload to ESP32:** Using Thonny or ampy, upload the **contents** of the generated `deploy/` directory to the root of your ESP32. Do not select the files individually from an expanded folder in Thonny, or Thonny will flatten the directory structure and break the OS. Highlight the 5 core items (`boot.py`, `core`, `hal`, `main.py`, `shard_profile.json`) inside `deploy/` and upload them together.

> [!WARNING]
> **Thonny IDE Gotchas & Silent Boots:**
> If you click the **Red Stop Button** in Thonny, it issues a "soft reboot" but intentionally sends an interrupt that **blocks `main.py` from executing natively**. This traps you at the `>>>` prompt and makes it look like the OS failed to boot silently.
> To see VorpaLine OS boot automatically, you must either click the **Green Play Button** while `main.py` is open, or physically press the **RESET** button on your ESP32 board.

## Hardware Wiring

Connect your host device to the ESP32:
* **Cyberdeck Bridge (UART):** UART IDs and pins are dynamically assigned based on your board selection in `hal/boards/`. Ensure common ground and appropriate voltage logic levels (3.3V).
* **ROS 2 USB Bridge:** Standard USB data pins.

## Configuration

Profiles are stored in the `profiles/` directory. The `build_shard.py` tool fuses the selected board type into the active profile and outputs it as `shard_profile.json` in the `deploy/` folder. 

Example (`ros2_shard.json`):
```json
{
  "shard_id": "ROS2_BRIDGE_001",
  "role_class": "core.roles.ros2_shard.Ros2Shard",
  "board_type": "adafruit_metro_esp32_s2",
  "active_modules": [
    "sys", 
    "machine",
    "hal.usb_bridge"
  ]
}
```

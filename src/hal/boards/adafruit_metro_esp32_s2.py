# Adafruit Metro ESP32-S2 Express Static Pinout & Direct Memory-Mapped Register Access
# Hardware-level definitions optimized with Viper emitters and inlined constants.

# pyrefly: ignore [missing-import]
import micropython

try:
    from micropython import const
except ImportError:
    const = lambda x: x

# Static Pin Mappings (Inlined constants - zero heap RAM)
ONBOARD_LED = const(42)   # GPIO42 onboard Red LED
LED_PIN_MASK = const(1 << (42 - 32)) # Shifted for GPIO_OUT1_REG

# Common Peripheral Pins (Default for Adafruit Metro ESP32-S2)
TX0         = const(37)
RX0         = const(38)
UART2_TX    = const(17) # Custom
UART2_RX    = const(16) # Custom
I2C_SDA     = const(33)
I2C_SCL     = const(34)
SPI_MOSI    = const(35)
SPI_MISO    = const(37)
SPI_CLK     = const(36)
SPI_CS      = const(5)

# ESP32-S2 Hardware Memory-Mapped Register Base & Offsets
# Reference: ESP32-S2 Technical Reference Manual
# Base address for ESP32-S2 GPIO is 0x3F404000
GPIO_OUT_REG         = const(0x3F404004) # Output value (Read/Write) for pins 0-31
GPIO_OUT_W1TS_REG    = const(0x3F404008) # Write 1 to Set bit (High) for pins 0-31
GPIO_OUT_W1TC_REG    = const(0x3F40400C) # Write 1 to Clear bit (Low) for pins 0-31
GPIO_ENABLE_REG      = const(0x3F404020) # Output enable register for pins 0-31
GPIO_ENABLE_W1TS_REG = const(0x3F404024) # Write 1 to Enable output for pins 0-31
GPIO_ENABLE_W1TC_REG = const(0x3F404028) # Write 1 to Disable output for pins 0-31
GPIO_IN_REG          = const(0x3F40403C) # Input value (Read-only) for pins 0-31

# Registers for pins 32-53
GPIO_OUT1_REG         = const(0x3F404010)
GPIO_OUT1_W1TS_REG    = const(0x3F404014)
GPIO_OUT1_W1TC_REG    = const(0x3F404018)
GPIO_ENABLE1_REG      = const(0x3F40402C)
GPIO_ENABLE1_W1TS_REG = const(0x3F404030)
GPIO_ENABLE1_W1TC_REG = const(0x3F404034)
GPIO_IN1_REG          = const(0x3F404040)

# ---------------------------------------------------------------------------
# High-Speed Viper Register Manipulators (Single-cycle / Sub-microsecond)
# Note: For pins > 31 (like LED 42), the '1' registers must be used.
# ---------------------------------------------------------------------------

@micropython.viper
def gpio_fast_enable(pin_mask: int):
    """Enables output driver for given pin bitmask (pins 0-31)."""
    p = ptr32(GPIO_ENABLE_W1TS_REG)
    p[0] = pin_mask

@micropython.viper
def gpio_fast_enable_high(pin_mask: int):
    """Enables output driver for given pin bitmask (pins 32-53)."""
    p = ptr32(GPIO_ENABLE1_W1TS_REG)
    p[0] = pin_mask

@micropython.viper
def gpio_fast_set(pin_mask: int):
    """Sets GPIO pins HIGH (pins 0-31)."""
    p = ptr32(GPIO_OUT_W1TS_REG)
    p[0] = pin_mask

@micropython.viper
def gpio_fast_set_high(pin_mask: int):
    """Sets GPIO pins HIGH (pins 32-53)."""
    p = ptr32(GPIO_OUT1_W1TS_REG)
    p[0] = pin_mask

@micropython.viper
def gpio_fast_clear(pin_mask: int):
    """Sets GPIO pins LOW (pins 0-31)."""
    p = ptr32(GPIO_OUT_W1TC_REG)
    p[0] = pin_mask

@micropython.viper
def gpio_fast_clear_high(pin_mask: int):
    """Sets GPIO pins LOW (pins 32-53)."""
    p = ptr32(GPIO_OUT1_W1TC_REG)
    p[0] = pin_mask

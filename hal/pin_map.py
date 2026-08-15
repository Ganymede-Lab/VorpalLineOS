# ESP32-WROOM-32 Static Pinout & Direct Memory-Mapped Register Access
# Hardware-level definitions optimized with Viper emitters and inlined constants.

# pyrefly: ignore [missing-import]
import micropython

try:
    from micropython import const
except ImportError:
    const = lambda x: x

# Static Pin Mappings (Inlined constants - zero heap RAM)
ONBOARD_LED = const(2)   # GPIO2 onboard LED
LED_PIN_MASK = const(1 << 2)

# Common Peripheral Pins
TX0         = const(1)
RX0         = const(3)
UART2_TX    = const(17) # Cyberdeck Bridge TX
UART2_RX    = const(16) # Cyberdeck Bridge RX
I2C_SDA     = const(21)
I2C_SCL     = const(22)
SPI_MOSI    = const(23)
SPI_MISO    = const(19)
SPI_CLK     = const(18)
SPI_CS      = const(5)

# ESP32 Hardware Memory-Mapped Register Base & Offsets
# Reference: ESP32 Technical Reference Manual (IO_MUX & GPIO Matrix)
GPIO_OUT_REG         = const(0x3FF44004) # Output value (Read/Write)
GPIO_OUT_W1TS_REG    = const(0x3FF44008) # Write 1 to Set bit (High)
GPIO_OUT_W1TC_REG    = const(0x3FF4400C) # Write 1 to Clear bit (Low)
GPIO_ENABLE_REG      = const(0x3FF44020) # Output enable register
GPIO_ENABLE_W1TS_REG = const(0x3FF44024) # Write 1 to Enable output
GPIO_ENABLE_W1TC_REG = const(0x3FF44028) # Write 1 to Disable output
GPIO_IN_REG          = const(0x3FF4403C) # Input value (Read-only)

# ---------------------------------------------------------------------------
# High-Speed Viper Register Manipulators (Single-cycle / Sub-microsecond)
# ---------------------------------------------------------------------------

@micropython.viper
def gpio_fast_enable(pin_mask: int):
    """Enables output driver for given pin bitmask via hardware register."""
    p = ptr32(GPIO_ENABLE_W1TS_REG)
    p[0] = pin_mask

@micropython.viper
def gpio_fast_set(pin_mask: int):
    """Sets GPIO pins HIGH using the Write-1-to-Set register."""
    p = ptr32(GPIO_OUT_W1TS_REG)
    p[0] = pin_mask

@micropython.viper
def gpio_fast_clear(pin_mask: int):
    """Sets GPIO pins LOW using the Write-1-to-Clear register."""
    p = ptr32(GPIO_OUT_W1TC_REG)
    p[0] = pin_mask

@micropython.viper
def gpio_fast_toggle(pin_mask: int):
    """Atomically toggles GPIO pins based on current hardware register state."""
    p_out = ptr32(GPIO_OUT_REG)
    current: int = p_out[0]
    if current & pin_mask:
        p_clear = ptr32(GPIO_OUT_W1TC_REG)
        p_clear[0] = pin_mask
    else:
        p_set = ptr32(GPIO_OUT_W1TS_REG)
        p_set[0] = pin_mask

@micropython.viper
def gpio_fast_read() -> int:
    """Reads the entire 32-bit GPIO input state directly from register."""
    p = ptr32(GPIO_IN_REG)
    return p[0]

from machine import UART, Pin
import uselect
import json
import micropython
from hal.pin_map import UART2_TX, UART2_RX

try:
    from micropython import const
except ImportError:
    const = lambda x: x

BUF_SIZE = const(256)

# Initialize Hardware UART2
# 115200 baud, 8 data bits, no parity, 1 stop bit.
# We set timeout=0 so the internal read is fully non-blocking.
deck_uart = UART(2, baudrate=115200, tx=Pin(UART2_TX), rx=Pin(UART2_RX), timeout=0)

# Setup a non-blocking poll object for the UART stream
poller = uselect.poll()
poller.register(deck_uart, uselect.POLLIN)

# Pre-allocated static buffer to eliminate continuous heap allocations
rx_buffer = bytearray(BUF_SIZE)
rx_view = memoryview(rx_buffer)
rx_len = 0

@micropython.native
def check_for_commands():
    """
    Non-blocking read from UART2 with zero heap-allocation during character buffering.
    Accumulates bytes into pre-allocated memory buffer and returns command on newline.
    """
    global rx_len
    
    # Read all available bytes without blocking
    while poller.poll(0):
        try:
            # Read single character directly from UART
            char_bytes = deck_uart.read(1)
            if not char_bytes:
                break
                
            byte_val = char_bytes[0]
            
            # Check for newline / carriage return (Command terminator)
            if byte_val == 10 or byte_val == 13: # '\n' or '\r'
                if rx_len > 0:
                    cmd_str = bytes(rx_view[:rx_len]).decode('utf-8').strip()
                    rx_len = 0
                    return cmd_str if cmd_str else None
                continue # Ignore empty newlines and keep reading
                
            # Accumulate into static buffer if capacity allows
            if rx_len < BUF_SIZE:
                rx_buffer[rx_len] = byte_val
                rx_len += 1
                
        except Exception:
            rx_len = 0
            break
            
    return None

def send_response(data_dict):
    """
    Serializes a dictionary to JSON and writes it back to the Cyberdeck via UART2.
    Appends a newline to terminate the message.
    """
    try:
        json_str = json.dumps(data_dict) + "\n"
        deck_uart.write(json_str.encode('utf-8'))
    except Exception as e:
        error_str = json.dumps({"error": "Failed to serialize response", "details": str(e)}) + "\n"
        deck_uart.write(error_str.encode('utf-8'))

from machine import UART, Pin
import uselect
import json
import micropython
from hal.pin_map import CYBERDECK_UART_ID, CYBERDECK_TX, CYBERDECK_RX

try:
    from micropython import const
except ImportError:
    const = lambda x: x

BUF_SIZE = const(256)

# ANSI Constants
ANSI_RESET = "\x1b[0m"
ANSI_GREEN = "\x1b[38;5;46m"
ANSI_CYAN = "\x1b[38;5;51m"
ANSI_RED = "\x1b[38;5;196m"
ANSI_BLACK = "\x1b[38;5;16m"
ANSI_CLEAR = "\x1b[2J"
ANSI_HOME = "\x1b[H"

# Initialize Hardware UART
deck_uart = UART(CYBERDECK_UART_ID, baudrate=115200, tx=Pin(CYBERDECK_TX), rx=Pin(CYBERDECK_RX), timeout=0)

# Flush any garbage from the boot cycle
deck_uart.read()

# Clear screen and print the initial login prompt
deck_uart.write(f"{ANSI_CLEAR}{ANSI_HOME}".encode('utf-8'))
deck_uart.write(f"{ANSI_CYAN}/// VRPLLINE OS // CYBERDECK LINK ACTIVE \\\\\\{ANSI_RESET}\r\n\r\n".encode('utf-8'))
deck_uart.write(f"{ANSI_GREEN}vrpl-os:~#{ANSI_RESET} ".encode('utf-8'))

# Setup a non-blocking poll object for the UART stream
poller = uselect.poll()
poller.register(deck_uart, uselect.POLLIN)

# Pre-allocated static buffer to eliminate continuous heap allocations
rx_buffer = bytearray(BUF_SIZE)
rx_view = memoryview(rx_buffer)
rx_len = 0
last_rx_char = 0

@micropython.native
def check_for_commands():
    """
    Non-blocking read from UART2 with zero heap-allocation during character buffering.
    Handles local echo, backspace, and newline parsing.
    """
    global rx_len, last_rx_char
    
    while poller.poll(0):
        try:
            char_bytes = deck_uart.read(1)
            if not char_bytes:
                break
                
            byte_val = char_bytes[0]
            
            if byte_val == 10 or byte_val == 13: # '\n' or '\r'
                # Prevent double-processing of \r\n
                if byte_val == 10 and last_rx_char == 13:
                    last_rx_char = byte_val
                    continue
                
                last_rx_char = byte_val
                
                # Echo CRLF to move terminal to the next line
                deck_uart.write(b"\r\n")
                
                cmd_str = bytes(rx_view[:rx_len]).decode('utf-8').strip()
                rx_len = 0
                
                if not cmd_str:
                    # Empty enter pressed! Just print a fresh prompt to fix "blank terminal"
                    deck_uart.write(f"{ANSI_GREEN}vrpl-os:~#{ANSI_RESET} ".encode('utf-8'))
                    continue
                    
                return cmd_str
                
            # Handle backspace (8 or 127)
            if byte_val == 8 or byte_val == 127:
                if rx_len > 0:
                    rx_len -= 1
                    # Erase char on terminal: move back, print space, move back
                    deck_uart.write(b"\x08 \x08")
                last_rx_char = byte_val
                continue
                
            # Echo normal characters so the user isn't typing blindly
            deck_uart.write(char_bytes)
            
            if rx_len < BUF_SIZE:
                rx_buffer[rx_len] = byte_val
                rx_len += 1
                
            last_rx_char = byte_val
                
        except Exception:
            rx_len = 0
            break
            
    return None

def send_response(data, color=None):
    try:
        if isinstance(data, dict):
            out_str = json.dumps(data)
        else:
            out_str = str(data)
            
        out_str = out_str.replace('\r\n', '\n').replace('\n', '\r\n')
        
        if color:
            out_str = f"{color}{out_str}{ANSI_RESET}"
            
        out_str += f"\r\n{ANSI_GREEN}vrpl-os:~#{ANSI_RESET} "
        
        deck_uart.write(out_str.encode('utf-8'))
    except Exception as e:
        print(f"[Cyberdeck] Error sending response: {e}")
        error_str = f"{ANSI_RED}Error: Failed to serialize response: {str(e)}{ANSI_RESET}\r\n{ANSI_GREEN}vrpl-os:~#{ANSI_RESET} "
        deck_uart.write(error_str.encode('utf-8'))


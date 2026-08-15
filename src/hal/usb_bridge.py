import sys
import uselect
import json
import micropython

try:
    from micropython import const
except ImportError:
    const = lambda x: x

BUF_SIZE = const(256)

# Setup a non-blocking poll object for standard input (USB CDC)
poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

# Pre-allocated static buffer to eliminate continuous heap allocations
rx_buffer = bytearray(BUF_SIZE)
rx_view = memoryview(rx_buffer)
rx_len = 0

@micropython.native
def check_for_commands():
    """
    Non-blocking read from sys.stdin via USB CDC.
    Accumulates bytes into pre-allocated memory buffer and returns JSON string on newline.
    """
    global rx_len
    
    while poller.poll(0):
        try:
            # Read single character directly from standard input
            char_str = sys.stdin.read(1)
            if not char_str:
                break
                
            byte_val = ord(char_str)
            
            # Check for newline / carriage return (Command terminator)
            if byte_val == 10 or byte_val == 13: # '\n' or '\r'
                if rx_len > 0:
                    cmd_str = bytes(rx_view[:rx_len]).decode('utf-8').strip()
                    rx_len = 0
                    return cmd_str if cmd_str else None
                continue
                
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
    Serializes a dictionary to JSON and writes it back to the USB Host via sys.stdout.
    Appends a newline to terminate the message.
    """
    try:
        json_str = json.dumps(data_dict) + "\n"
        sys.stdout.write(json_str)
    except Exception as e:
        error_str = json.dumps({"error": "Failed to serialize response", "details": str(e)}) + "\n"
        sys.stdout.write(error_str)

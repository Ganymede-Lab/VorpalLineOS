# main.py
# This script is automatically executed by MicroPython after boot.py finishes.

import gc
import time

# Brief delay to allow Native USB (CDC) boards like the ESP32-S2/S3 to 
# re-establish their serial connection with the host before printing.
time.sleep(1.5)

from core.vorpaline import VorpaLineOS

def main():
    # Final cleanup before passing control to the OS
    gc.collect()
    
    # Initialize and run the VorpaLine OS state machine
    os = VorpaLineOS()
    os.run()

if __name__ == '__main__':
    main()

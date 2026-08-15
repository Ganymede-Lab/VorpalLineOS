# main.py
# This script is automatically executed by MicroPython after boot.py finishes.

import gc
from core.vorpaline import VorpaLineOS

def main():
    # Final cleanup before passing control to the OS
    gc.collect()
    
    # Initialize and run the VorpaLine OS state machine
    os = VorpaLineOS()
    os.run()

if __name__ == '__main__':
    main()

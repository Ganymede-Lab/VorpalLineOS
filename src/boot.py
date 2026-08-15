import gc
import uos
import machine
import micropython

# Allocate emergency exception buffer for fail-safe debugging in ISRs/low RAM
try:
    micropython.alloc_emergency_exception_buf(128)
except AttributeError:
    pass

# Run garbage collection to ensure maximum free memory on startup
gc.collect()

# Mount the internal filesystem (MicroPython on ESP32 mounts it automatically)
# We can check the filesystem stat to ensure it is mounted
try:
    uos.stat('/')
    print("Filesystem mounted successfully.")
except OSError:
    print("Error: Filesystem not mounted.")



print("VorpaLine OS low-level boot complete.")
gc.collect()

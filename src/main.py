# main.py
# This script is automatically executed by MicroPython after boot.py finishes.

print("[DEBUG] main.py started")
import gc

try:
    print("[DEBUG] Attempting to import VorpaLineOS...")
    from core.vorpaline import VorpaLineOS
    print("[DEBUG] Import successful.")
except Exception as e:
    print(f"[CRITICAL ERROR] Failed to import VorpaLineOS: {e}")

def main():
    print("[DEBUG] Executing main()...")
    gc.collect()
    try:
        print("[DEBUG] Instantiating OS...")
        os = VorpaLineOS()
        print("[DEBUG] Running OS...")
        os.run()
    except Exception as e:
        print(f"[CRITICAL ERROR] OS Runtime Exception: {e}")

if __name__ == '__main__':
    print("[DEBUG] __name__ is __main__, calling main()")
    main()
else:
    print(f"[DEBUG] __name__ is {__name__}, skipping main()")

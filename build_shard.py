#!/usr/bin/env python3
import os
import sys
import shutil

PROFILES_DIR = "profiles"
ROOT_PROFILE = "shard_profile.json"

def main():
    print("==================================================")
    print("             VorpaLine OS Shard Builder           ")
    print("==================================================")
    
    if not os.path.exists(PROFILES_DIR):
        print(f"[ERROR] {PROFILES_DIR}/ directory not found.")
        return 1
        
    profiles = [f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
    if not profiles:
        print(f"[ERROR] No profiles found in {PROFILES_DIR}/")
        return 1
        
    print("\nSelect a shard profile to build:\n")
    for idx, p in enumerate(profiles):
        print(f"  [{idx + 1}] {p}")
        
    try:
        choice = input("\nEnter profile number: ")
        idx = int(choice) - 1
        if idx < 0 or idx >= len(profiles):
            print("[ERROR] Invalid selection.")
            return 1
            
        selected_profile = profiles[idx]
        src_path = os.path.join(PROFILES_DIR, selected_profile)
        
        # Copy to root
        shutil.copyfile(src_path, ROOT_PROFILE)
        print(f"\n[OK] Set active profile to: {selected_profile}")
        
        # Trigger compile
        print("Compiling Shard...\n")
        os.system(f"{sys.executable} compile_shards.py")
        
    except ValueError:
        print("[ERROR] Please enter a valid number.")
        return 1
    except KeyboardInterrupt:
        print("\nBuild cancelled.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

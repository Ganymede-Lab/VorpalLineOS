#!/usr/bin/env python3
import os
import sys
import shutil
import json

PROFILES_DIR = "profiles"
BOARDS_DIR = os.path.join("src", "hal", "boards")
DEPLOY_DIR = "deploy"
ROOT_PROFILE = os.path.join(DEPLOY_DIR, "shard_profile.json")
HAL_PIN_MAP = os.path.join("src", "hal", "pin_map.py")

def main():
    print("==================================================")
    print("             VorpaLine OS Shard Builder           ")
    print("==================================================")
    
    if not os.path.exists(PROFILES_DIR):
        print(f"[ERROR] {PROFILES_DIR}/ directory not found.")
        return 1
        
    if not os.path.exists(BOARDS_DIR):
        print(f"[ERROR] {BOARDS_DIR}/ directory not found.")
        return 1

    boards = sorted([f for f in os.listdir(BOARDS_DIR) if f.endswith(".py") and not f.startswith("__")])
    profiles = sorted([f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")])
    
    if not boards:
        print(f"[ERROR] No boards found in {BOARDS_DIR}/")
        return 1
    if not profiles:
        print(f"[ERROR] No profiles found in {PROFILES_DIR}/")
        return 1
        
    print("\nSelect a board:")
    for idx, b in enumerate(boards):
        print(f"  [{idx + 1}] {b.replace('.py', '')}")
        
    try:
        b_choice = input("\nEnter board number: ")
        b_idx = int(b_choice) - 1
        if b_idx < 0 or b_idx >= len(boards):
            print("[ERROR] Invalid selection.")
            return 1
        selected_board = boards[b_idx]
        
        print("\nSelect a shard profile:")
        for idx, p in enumerate(profiles):
            print(f"  [{idx + 1}] {p}")
            
        p_choice = input("\nEnter profile number: ")
        p_idx = int(p_choice) - 1
        if p_idx < 0 or p_idx >= len(profiles):
            print("[ERROR] Invalid selection.")
            return 1
            
        selected_profile = profiles[p_idx]
        
        # 1. Copy board to src/hal/pin_map.py
        board_src = os.path.join(BOARDS_DIR, selected_board)
        shutil.copyfile(board_src, HAL_PIN_MAP)
        board_name = selected_board.replace('.py', '')
        print(f"\n[OK] Set board to: {board_name}")
        
        # 2. Read profile, update board_type, write to deploy/
        os.makedirs(DEPLOY_DIR, exist_ok=True)
        prof_src = os.path.join(PROFILES_DIR, selected_profile)
        with open(prof_src, "r") as f:
            prof_data = json.load(f)
            
        prof_data["board_type"] = board_name
        
        with open(ROOT_PROFILE, "w") as f:
            json.dump(prof_data, f, indent=2)
            
        print(f"[OK] Set active profile to: {selected_profile} (in deploy/)")
        
        # Trigger compile
        print("\nCompiling Shard...\n")
        os.system(f"{sys.executable} compile_shards.py")
        
    except ValueError:
        print("[ERROR] Please enter a valid number.")
        return 1
    except KeyboardInterrupt:
        print("\nBuild cancelled.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

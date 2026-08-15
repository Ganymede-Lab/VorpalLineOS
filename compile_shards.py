#!/usr/bin/env python3
"""
VorpaLine OS - Shard & Core Bytecode Cross-Compiler
Compiles .py source files to optimized .mpy bytecode for ESP32 microcontrollers.
"""

import os
import sys
import subprocess
import shutil

TARGET_DIRS = ["src/core", "src/hal"]
DEPLOY_DIR = "deploy"

def check_mpy_cross():
    """Verify if mpy-cross is installed on the host system."""
    mpy_cmd = shutil.which("mpy-cross")
    if mpy_cmd:
        return mpy_cmd
    
    # Check user-level bin locations (macOS and Linux)
    user_paths = [
        os.path.expanduser("~/Library/Python/3.14/bin/mpy-cross"),
        os.path.expanduser("~/Library/Python/3.13/bin/mpy-cross"),
        os.path.expanduser("~/Library/Python/3.12/bin/mpy-cross"),
        os.path.expanduser("~/Library/Python/3.11/bin/mpy-cross"),
        os.path.expanduser("~/.local/bin/mpy-cross")
    ]
    for p in user_paths:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
            
    # Try python -m mpy_cross if installed as a pip module
    try:
        res = subprocess.run([sys.executable, "-m", "mpy_cross", "--version"], 
                             capture_output=True, text=True)
        if res.returncode == 0:
            return f"{sys.executable} -m mpy_cross"
    except Exception:
        pass
    
    return None

def compile_file(compiler_cmd, src_path, arch="xtensawin"):
    """Compiles a single .py file to .mpy targeting the ESP32 Xtensa architecture."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    rel_src = os.path.relpath(src_path, base_dir)
    
    if rel_src.startswith("src/"):
        rel_dest = rel_src[4:]
    else:
        rel_dest = rel_src
        
    mpy_dest = os.path.join(base_dir, DEPLOY_DIR, os.path.splitext(rel_dest)[0] + ".mpy")
    os.makedirs(os.path.dirname(mpy_dest), exist_ok=True)
    
    cmd = compiler_cmd.split() + [
        f"-march={arch}",
        "-O3", 
        "-s", os.path.basename(src_path), 
        src_path, 
        "-o", mpy_dest
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        orig_size = os.path.getsize(src_path)
        mpy_size = os.path.getsize(mpy_dest)
        reduction = (1 - mpy_size/orig_size) * 100
        print(f"  [OK] {rel_src} -> {os.path.relpath(mpy_dest, base_dir)} ({orig_size}B -> {mpy_size}B, {reduction:.1f}% reduction)")
        return True
    else:
        print(f"  [FAIL] {rel_src}: {res.stderr.strip()}")
        return False

def main():
    print("==================================================")
    print("       VorpaLine OS Bytecode Compiler (.mpy)      ")
    print("==================================================")
    
    compiler = check_mpy_cross()
    if not compiler:
        print("\n[ERROR] 'mpy-cross' is not installed.")
        print("To install mpy-cross on your computer, run:")
        print(f"    {sys.executable} -m pip install mpy-cross")
        print("\nOr install via homebrew / package manager:")
        print("    brew install micropython\n")
        return 1
    
    print(f"Using compiler: {compiler}\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(base_dir, DEPLOY_DIR), exist_ok=True)
    
    # Copy boot files
    print("Copying core boot files...")
    shutil.copyfile(os.path.join(base_dir, "src", "boot.py"), os.path.join(base_dir, DEPLOY_DIR, "boot.py"))
    shutil.copyfile(os.path.join(base_dir, "src", "main.py"), os.path.join(base_dir, DEPLOY_DIR, "main.py"))
    print("  [OK] src/boot.py -> deploy/boot.py")
    print("  [OK] src/main.py -> deploy/main.py\n")
    
    files_to_compile = []
    
    for dir_name in TARGET_DIRS:
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                # Ignore __pycache__, hidden dirs, and boards
                dirs[:] = [d for d in dirs if not d.startswith('__') and d != "boards"]
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        files_to_compile.append(os.path.join(root, file))
                        
    print(f"Found {len(files_to_compile)} module(s) to compile:\n")
    
    success_count = 0
    for file_path in files_to_compile:
        if compile_file(compiler, file_path):
            success_count += 1
            
    print(f"\nCompilation finished: {success_count}/{len(files_to_compile)} succeeded.")
    print("The deploy/ folder is ready to be uploaded to the ESP32 flash.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

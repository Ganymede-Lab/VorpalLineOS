#!/usr/bin/env python3
"""
VorpaLine OS - Shard & Core Bytecode Cross-Compiler
Compiles .py source files to optimized .mpy bytecode for ESP32 microcontrollers.
"""

import os
import sys
import subprocess
import shutil

TARGET_DIRS = ["core", "hal"]
ROOT_FILES = [] # boot.py and main.py typically remain .py on filesystem root

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
    mpy_path = os.path.splitext(src_path)[0] + ".mpy"
    cmd = compiler_cmd.split() + [
        f"-march={arch}",
        "-O3", 
        "-s", os.path.basename(src_path), 
        src_path, 
        "-o", mpy_path
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        orig_size = os.path.getsize(src_path)
        mpy_size = os.path.getsize(mpy_path)
        reduction = (1 - mpy_size/orig_size) * 100
        print(f"  [OK] {src_path} -> {mpy_path} ({orig_size}B -> {mpy_size}B, {reduction:.1f}% reduction)")
        return True
    else:
        print(f"  [FAIL] {src_path}: {res.stderr.strip()}")
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
    
    files_to_compile = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for dir_name in TARGET_DIRS:
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                # Ignore __pycache__ or hidden dirs
                dirs[:] = [d for d in dirs if not d.startswith('__')]
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        files_to_compile.append(os.path.join(root, file))
                    
    for root_file in ROOT_FILES:
        full_path = os.path.join(base_dir, root_file)
        if os.path.exists(full_path):
            files_to_compile.append(full_path)
            
    print(f"Found {len(files_to_compile)} module(s) to compile:\n")
    
    success_count = 0
    for file_path in files_to_compile:
        rel_path = os.path.relpath(file_path, base_dir)
        if compile_file(compiler, file_path):
            success_count += 1
            
    print(f"\nCompilation finished: {success_count}/{len(files_to_compile)} succeeded.")
    print("Pre-compiled .mpy files are ready to deploy to ESP32 flash.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

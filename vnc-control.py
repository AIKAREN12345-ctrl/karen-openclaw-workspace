#!/usr/bin/env python3
"""
VNC Mouse and Keyboard Control Script
Provides remote control capabilities via VNC connection
Uses vncdo command line tool
"""

import subprocess
import sys
import argparse

VNC_HOST = "localhost"
VNC_PORT = "5900"
VNC_PASSWORD = "Karen1234$"
VNCDO_PATH = r"C:\Users\Karen\AppData\Roaming\Python\Python311\Scripts\vncdo.exe"

def run_vncdo(commands):
    """Run vncdo with given commands"""
    cmd = [
        VNCDO_PATH,
        "-s", f"{VNC_HOST}::{VNC_PORT}",
        "-p", VNC_PASSWORD
    ] + commands
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[VNC Error] {result.stderr}")
        return False
    return True

def click(x, y, button=1):
    """Click at specific coordinates"""
    if run_vncdo(["move", str(x), str(y), "click", str(button)]):
        print(f"[VNC] Clicked at ({x}, {y}) with button {button}")
        return True
    return False

def move(x, y):
    """Move mouse to coordinates"""
    if run_vncdo(["move", str(x), str(y)]):
        print(f"[VNC] Moved to ({x}, {y})")
        return True
    return False

def type_text(text):
    """Type text"""
    if run_vncdo(["type", text]):
        print(f"[VNC] Typed: {text}")
        return True
    return False

def key(key_name):
    """Press a key (e.g., 'ctrl', 'alt', 'del', 'return')"""
    if run_vncdo(["key", key_name]):
        print(f"[VNC] Pressed key: {key_name}")
        return True
    return False

def key_combo(*keys):
    """Press key combination (e.g., 'ctrl', 'alt', 'del')"""
    combo = "-".join(keys)
    if run_vncdo(["key", combo]):
        print(f"[VNC] Key combo: {combo}")
        return True
    return False

def capture(filename):
    """Capture screenshot"""
    import os
    # Save to workspace directory
    workspace = r"C:\Users\Karen\.openclaw\workspace"
    filepath = os.path.join(workspace, filename)
    if run_vncdo(["capture", filepath]):
        print(f"[VNC] Screenshot saved: {filepath}")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description='VNC Control Tool')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Click command
    click_parser = subparsers.add_parser('click', help='Click at coordinates')
    click_parser.add_argument('x', type=int, help='X coordinate')
    click_parser.add_argument('y', type=int, help='Y coordinate')
    click_parser.add_argument('--button', type=int, default=1, help='Mouse button (1=left, 2=middle, 3=right)')
    
    # Move command
    move_parser = subparsers.add_parser('move', help='Move mouse to coordinates')
    move_parser.add_argument('x', type=int, help='X coordinate')
    move_parser.add_argument('y', type=int, help='Y coordinate')
    
    # Type command
    type_parser = subparsers.add_parser('type', help='Type text')
    type_parser.add_argument('text', help='Text to type')
    
    # Key command
    key_parser = subparsers.add_parser('key', help='Press key or combo')
    key_parser.add_argument('keys', nargs='+', help='Keys to press (e.g., ctrl alt del)')
    
    # Capture command
    capture_parser = subparsers.add_parser('capture', help='Capture screenshot')
    capture_parser.add_argument('filename', help='Output filename')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    success = False
    if args.command == 'click':
        success = click(args.x, args.y, args.button)
    elif args.command == 'move':
        success = move(args.x, args.y)
    elif args.command == 'type':
        success = type_text(args.text)
    elif args.command == 'key':
        if len(args.keys) == 1:
            success = key(args.keys[0])
        else:
            success = key_combo(*args.keys)
    elif args.command == 'capture':
        success = capture(args.filename)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

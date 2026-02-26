#!/usr/bin/env python3
"""
VNC Mouse and Keyboard Control Script
Provides remote control capabilities via VNC connection
"""

import sys
import argparse
from vncdotool import api

def click(client, x, y, button=1):
    """Click at specific coordinates"""
    client.mouseMove(x, y)
    client.mouseDown(button)
    client.mouseUp(button)
    print(f"[VNC] Clicked at ({x}, {y}) with button {button}")

def type_text(client, text):
    """Type text"""
    client.keyPress(text)
    print(f"[VNC] Typed: {text}")

def key_combo(client, keys):
    """Press key combination (e.g., 'ctrl', 'alt', 'del')"""
    client.keyDown(*keys)
    client.keyUp(*keys)
    print(f"[VNC] Key combo: {'+'.join(keys)}")

def main():
    parser = argparse.ArgumentParser(description='VNC Control Tool')
    parser.add_argument('--host', default='localhost', help='VNC host')
    parser.add_argument('--port', type=int, default=5900, help='VNC port')
    parser.add_argument('--password', default='Karen1234$', help='VNC password')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Click command
    click_parser = subparsers.add_parser('click', help='Click at coordinates')
    click_parser.add_argument('x', type=int, help='X coordinate')
    click_parser.add_argument('y', type=int, help='Y coordinate')
    click_parser.add_argument('--button', type=int, default=1, help='Mouse button (1=left, 2=middle, 3=right)')
    
    # Type command
    type_parser = subparsers.add_parser('type', help='Type text')
    type_parser.add_argument('text', help='Text to type')
    
    # Key command
    key_parser = subparsers.add_parser('key', help='Press key combination')
    key_parser.add_argument('keys', nargs='+', help='Keys to press (e.g., ctrl alt del)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Connect to VNC
    print(f"[VNC] Connecting to {args.host}:{args.port}...")
    client = api.connect(f"{args.host}::{args.port}", password=args.password)
    print("[VNC] Connected")
    
    try:
        if args.command == 'click':
            click(client, args.x, args.y, args.button)
        elif args.command == 'type':
            type_text(client, args.text)
        elif args.command == 'key':
            key_combo(client, args.keys)
    finally:
        client.disconnect()
        print("[VNC] Disconnected")

if __name__ == '__main__':
    main()

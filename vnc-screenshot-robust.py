#!/usr/bin/env python3
"""
Robust VNC Screenshot - Fixed struct parsing
Uses correct RFB protocol format for UltraVNC
"""

import socket
import struct
import time
from PIL import Image

def vnc_screenshot_robust(host='localhost', port=5900, password='Karen1234$', output='vnc_screenshot.png'):
    sock = None
    try:
        print(f"[VNC] Connecting to {host}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((host, port))
        
        # 1. Protocol Version Handshake
        server_version = b''
        while b'\n' not in server_version:
            server_version += sock.recv(1)
        print(f"[VNC] Server: {server_version.decode('ascii', errors='ignore').strip()}")
        
        # Send our version
        sock.send(b'RFB 003.008\n')
        
        # 2. Security Handshake
        security_types = sock.recv(1)
        if not security_types:
            print("[VNC] No security types received")
            return False
        
        num_types = security_types[0]
        print(f"[VNC] Security types offered: {num_types}")
        
        if num_types == 0:
            # Error from server
            error_len = struct.unpack('>I', sock.recv(4))[0]
            error_msg = sock.recv(error_len).decode('utf-8', errors='ignore')
            print(f"[VNC] Server error: {error_msg}")
            return False
        
        types = list(sock.recv(num_types))
        print(f"[VNC] Available: {types}")
        
        # Choose VNC auth (type 2) if available
        if 2 not in types:
            print("[VNC] VNC auth (type 2) not available")
            return False
        
        sock.send(bytes([2]))
        
        # 3. VNC Authentication
        challenge = sock.recv(16)
        if len(challenge) != 16:
            print(f"[VNC] Invalid challenge length: {len(challenge)}")
            return False
        
        print("[VNC] Authenticating...")
        
        # DES encrypt challenge with password
        from Crypto.Cipher import DES
        
        # VNC password is max 8 chars, padded with nulls
        key = password.encode('ascii')[:8].ljust(8, b'\x00')
        
        # VNC uses bit-reversed DES key
        def reverse_bits(b):
            return int('{:08b}'.format(b)[::-1], 2)
        
        key = bytes([reverse_bits(b) for b in key])
        
        cipher = DES.new(key, DES.MODE_ECB)
        response = cipher.encrypt(challenge)
        sock.send(response)
        
        # Read auth result (4 bytes, big-endian)
        auth_result_data = sock.recv(4)
        if len(auth_result_data) != 4:
            print(f"[VNC] Invalid auth result length: {len(auth_result_data)}")
            return False
        
        auth_result = struct.unpack('>I', auth_result_data)[0]
        
        if auth_result != 0:
            print(f"[VNC] Authentication failed: {auth_result}")
            return False
        
        print("[VNC] Authenticated!")
        
        # 4. ClientInit - request shared session
        sock.send(bytes([1]))  # shared flag = 1
        
        # 5. ServerInit - read framebuffer info
        # Width (2 bytes, big-endian)
        width_data = sock.recv(2)
        if len(width_data) != 2:
            print("[VNC] Failed to read width")
            return False
        width = struct.unpack('>H', width_data)[0]
        
        # Height (2 bytes, big-endian)
        height_data = sock.recv(2)
        if len(height_data) != 2:
            print("[VNC] Failed to read height")
            return False
        height = struct.unpack('>H', height_data)[0]
        
        print(f"[VNC] Screen: {width}x{height}")
        
        # Pixel format (16 bytes)
        pixel_format = sock.recv(16)
        if len(pixel_format) != 16:
            print("[VNC] Failed to read pixel format")
            return False
        
        # Desktop name length (4 bytes, big-endian)
        name_len_data = sock.recv(4)
        if len(name_len_data) != 4:
            print("[VNC] Failed to read name length")
            return False
        name_len = struct.unpack('>I', name_len_data)[0]
        
        # Desktop name
        if name_len > 0:
            desktop_name = sock.recv(name_len).decode('utf-8', errors='ignore')
            print(f"[VNC] Desktop: {desktop_name}")
        
        # Validate dimensions
        if width == 0 or height == 0 or width > 7680 or height > 4320:
            print(f"[VNC] Invalid dimensions: {width}x{height}")
            # Try common resolutions
            width, height = 1920, 1080
            print(f"[VNC] Using fallback: {width}x{height}")
        
        # 6. Set Pixel Format (32-bit RGB)
        sock.send(bytes([0]))  # SetPixelFormat
        sock.send(bytes([0, 0, 0]))  # padding
        # bits-per-pixel, depth, big-endian, true-color
        sock.send(struct.pack('BBBB', 32, 24, 0, 1))
        # max red, green, blue (2 bytes each, big-endian)
        sock.send(struct.pack('>HHH', 255, 255, 255))
        # shift red, green, blue
        sock.send(struct.pack('BBB', 16, 8, 0))
        sock.send(bytes([0, 0, 0]))  # padding
        
        # 7. Set Encodings - Raw only for reliability
        sock.send(bytes([2]))  # SetEncodings
        sock.send(bytes([0]))  # padding
        sock.send(struct.pack('>H', 1))  # 1 encoding
        sock.send(struct.pack('>i', 0))  # Raw encoding
        
        time.sleep(0.2)  # Let server process
        
        # 8. Request Framebuffer Update
        print("[VNC] Requesting screen capture...")
        sock.send(bytes([3]))  # FramebufferUpdateRequest
        sock.send(bytes([0]))  # incremental = 0 (full refresh)
        # x, y, width, height (all 2-byte big-endian)
        sock.send(struct.pack('>HHHH', 0, 0, width, height))
        
        # 9. Read Framebuffer Update
        sock.settimeout(10)
        
        # Message type (1 byte)
        msg_type_data = sock.recv(1)
        if len(msg_type_data) != 1:
            print("[VNC] No message received")
            return False
        
        msg_type = msg_type_data[0]
        if msg_type != 0:
            print(f"[VNC] Unexpected message type: {msg_type}")
            return False
        
        # Padding (1 byte)
        sock.recv(1)
        
        # Number of rectangles (2 bytes, big-endian)
        num_rects_data = sock.recv(2)
        if len(num_rects_data) != 2:
            print("[VNC] Failed to read rectangle count")
            return False
        num_rects = struct.unpack('>H', num_rects_data)[0]
        
        print(f"[VNC] Receiving {num_rects} rectangles...")
        
        # Create image
        img = Image.new('RGB', (width, height), color=(0, 0, 0))
        
        for rect_idx in range(min(num_rects, 100)):
            # Rectangle header (12 bytes)
            rect_header = b''
            while len(rect_header) < 12:
                chunk = sock.recv(12 - len(rect_header))
                if not chunk:
                    break
                rect_header += chunk
            
            if len(rect_header) < 12:
                print(f"[VNC] Incomplete rectangle header")
                break
            
            x = struct.unpack('>H', rect_header[0:2])[0]
            y = struct.unpack('>H', rect_header[2:4])[0]
            w = struct.unpack('>H', rect_header[4:6])[0]
            h = struct.unpack('>H', rect_header[6:8])[0]
            encoding = struct.unpack('>i', rect_header[8:12])[0]
            
            if w == 0 or h == 0:
                continue
            
            if encoding != 0:
                print(f"[VNC] Skipping non-raw encoding: {encoding}")
                continue
            
            # Read raw pixel data (BGRX format, 4 bytes per pixel)
            expected_bytes = w * h * 4
            pixels = b''
            sock.settimeout(5)
            
            while len(pixels) < expected_bytes:
                try:
                    chunk = sock.recv(min(65536, expected_bytes - len(pixels)))
                    if not chunk:
                        break
                    pixels += chunk
                except socket.timeout:
                    print(f"[VNC] Timeout reading pixels")
                    break
            
            # Fill image (convert BGRX to RGB)
            for row in range(min(h, height - y)):
                for col in range(min(w, width - x)):
                    idx = (row * w + col) * 4
                    if idx + 2 < len(pixels):
                        b, g, r = pixels[idx], pixels[idx+1], pixels[idx+2]
                        img.putpixel((x + col, y + row), (r, g, b))
            
            if rect_idx % 10 == 0:
                print(f"[VNC] Processed {rect_idx}/{num_rects} rectangles...")
        
        # Save image
        img.save(output, 'PNG')
        print(f"[VNC] Screenshot saved: {output}")
        print(f"[VNC] Dimensions: {width}x{height}")
        return True
        
    except socket.timeout:
        print("[VNC] Connection timed out")
        return False
    except Exception as e:
        print(f"[VNC] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if sock:
            sock.close()
            print("[VNC] Disconnected")

if __name__ == '__main__':
    success = vnc_screenshot_robust()
    exit(0 if success else 1)

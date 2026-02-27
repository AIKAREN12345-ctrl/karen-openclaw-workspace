#!/usr/bin/env python3
"""VNC Screen Recorder - Robust Version"""
import argparse
import sys
import time
import os
import struct
import socket
from datetime import datetime
from pathlib import Path

try:
    import numpy as np
    import cv2
    from PIL import Image
    from Crypto.Cipher import DES
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

class VNCRecorder:
    def __init__(self, host="localhost", port=5900, password=None, fps=10):
        self.host = host
        self.port = port
        self.password = password
        self.fps = fps
        self.frame_delay = 1.0 / fps
        self.sock = None
        self.width = 0
        self.height = 0
        
    def connect(self):
        try:
            print(f"[VNC] Connecting to {self.host}:{self.port}...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(15)
            self.sock.connect((self.host, self.port))
            
            # Protocol version
            server_version = b''
            while b'\n' not in server_version:
                server_version += self.sock.recv(1)
            print(f"[VNC] Server: {server_version.decode('ascii', errors='ignore').strip()}")
            self.sock.send(b'RFB 003.008\n')
            
            # Security
            num_types = self.sock.recv(1)[0]
            types = list(self.sock.recv(num_types))
            
            if 2 not in types:
                print("[VNC] VNC auth not available")
                return False
            
            self.sock.send(bytes([2]))
            
            # Auth
            challenge = self.sock.recv(16)
            key = self.password.encode('ascii')[:8].ljust(8, b'\x00')
            key = bytes([int('{:08b}'.format(b)[::-1], 2) for b in key])
            
            cipher = DES.new(key, DES.MODE_ECB)
            self.sock.send(cipher.encrypt(challenge))
            
            auth_result = struct.unpack('>I', self.sock.recv(4))[0]
            if auth_result != 0:
                print(f"[VNC] Auth failed")
                return False
            
            print("[VNC] Authenticated!")
            
            # Client init
            self.sock.send(bytes([1]))
            
            # Server init - BIG ENDIAN
            self.width = struct.unpack('>H', self.sock.recv(2))[0]
            self.height = struct.unpack('>H', self.sock.recv(2))[0]
            self.sock.recv(16)  # pixel format
            name_len = struct.unpack('>I', self.sock.recv(4))[0]
            if name_len > 0:
                self.sock.recv(name_len)
            
            print(f"[VNC] Screen: {self.width}x{self.height}")
            
            if self.width == 0 or self.height == 0:
                self.width, self.height = 1920, 1080
            
            # Set pixel format
            self.sock.send(bytes([0, 0, 0, 0]))
            self.sock.send(struct.pack('BBBB', 32, 24, 0, 1))
            self.sock.send(struct.pack('>HHH', 255, 255, 255))
            self.sock.send(struct.pack('BBB', 16, 8, 0))
            self.sock.send(bytes([0, 0, 0]))
            
            # Set encodings
            self.sock.send(bytes([2, 0]))
            self.sock.send(struct.pack('>H', 1))
            self.sock.send(struct.pack('>i', 0))
            
            time.sleep(0.2)
            return True
            
        except Exception as e:
            print(f"[VNC] Error: {e}")
            return False
    
    def capture_frame(self):
        try:
            self.sock.send(bytes([3, 0]))
            self.sock.send(struct.pack('>HHHH', 0, 0, self.width, self.height))
            
            self.sock.settimeout(5)
            msg_type = self.sock.recv(1)
            if len(msg_type) < 1 or msg_type[0] != 0:
                return None
            
            self.sock.recv(1)
            num_rects = struct.unpack('>H', self.sock.recv(2))[0]
            
            img = Image.new('RGB', (self.width, self.height), color=(0, 0, 0))
            
            for _ in range(min(num_rects, 50)):
                rect_header = b''
                while len(rect_header) < 12:
                    chunk = self.sock.recv(12 - len(rect_header))
                    if not chunk:
                        break
                    rect_header += chunk
                
                if len(rect_header) < 12:
                    break
                
                x = struct.unpack('>H', rect_header[0:2])[0]
                y = struct.unpack('>H', rect_header[2:4])[0]
                w = struct.unpack('>H', rect_header[4:6])[0]
                h = struct.unpack('>H', rect_header[6:8])[0]
                encoding = struct.unpack('>i', rect_header[8:12])[0]
                
                if w == 0 or h == 0 or encoding != 0:
                    continue
                
                expected = w * h * 4
                pixels = b''
                self.sock.settimeout(3)
                
                while len(pixels) < expected:
                    try:
                        chunk = self.sock.recv(min(32768, expected - len(pixels)))
                        if not chunk:
                            break
                        pixels += chunk
                    except socket.timeout:
                        break
                
                for row in range(min(h, self.height - y)):
                    for col in range(min(w, self.width - x)):
                        idx = (row * w + col) * 4
                        if idx + 2 < len(pixels):
                            b, g, r = pixels[idx], pixels[idx+1], pixels[idx+2]
                            img.putpixel((x + col, y + row), (r, g, b))
            
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            return frame
            
        except Exception as e:
            return None
    
    def record(self, duration, output_file):
        if not self.sock:
            return False
        
        print(f"[VNC] Recording {duration}s at {self.fps} FPS...")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, self.fps, (self.width, self.height))
        
        if not out.isOpened():
            print("[VNC] Failed to open video writer")
            return False
        
        start_time = time.time()
        frames = 0
        
        try:
            while (time.time() - start_time) < duration:
                frame_start = time.time()
                
                frame = self.capture_frame()
                if frame is not None:
                    out.write(frame)
                    frames += 1
                
                elapsed = time.time() - start_time
                if int(elapsed) % 5 == 0 and int(elapsed) > 0:
                    print(f"[VNC] {int(elapsed)}s / {duration}s ({frames} frames)")
                
                sleep_time = self.frame_delay - (time.time() - frame_start)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        except KeyboardInterrupt:
            pass
        finally:
            out.release()
        
        actual = time.time() - start_time
        print(f"[VNC] Done: {frames} frames in {actual:.1f}s")
        if os.path.exists(output_file):
            print(f"[VNC] Size: {os.path.getsize(output_file) / 1024 / 1024:.1f} MB")
        return True
    
    def disconnect(self):
        if self.sock:
            self.sock.close()
            print("[VNC] Disconnected")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=5)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"vnc_recording_{timestamp}.mp4"
    
    recorder = VNCRecorder(password="Karen1234$")
    
    if recorder.connect():
        try:
            recorder.record(args.duration, args.output)
        finally:
            recorder.disconnect()

if __name__ == "__main__":
    main()

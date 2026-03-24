# Simple HTTP Server for Karen Dashboard
# Run this script to serve the dashboard on localhost:8080

import http.server
import socketserver
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Serving Karen Dashboard at http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()

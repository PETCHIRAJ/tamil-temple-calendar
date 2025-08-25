#!/usr/bin/env python3
"""
Development Server for Tamil Temple Guide Demo UI
==================================================
Simple HTTP server with CORS support for local development
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 8080
DIRECTORY = "."  # Serve from demo-ui root to access both v2-current and data folders

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        sys.stderr.write(f"[{self.log_date_time_string()}] {format%args}\n")

def main():
    """Start the development server"""
    print("=" * 60)
    print("🛕 Tamil Temple Guide - Development Server")
    print("=" * 60)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    print(f"📁 Serving directory: {DIRECTORY}")
    print(f"🌐 Server starting on: http://localhost:{PORT}")
    print("=" * 60)
    print("📱 Access URLs:")
    print(f"   Local:    http://localhost:{PORT}/v2-current/")
    print(f"   Network:  http://0.0.0.0:{PORT}/v2-current/")
    print("=" * 60)
    print("Press Ctrl+C to stop the server\n")
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Server stopped")
            sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple HTTP server for Temple Verification UI
Serves files with CORS headers to allow local file access
"""

import http.server
import socketserver
import os

PORT = 8002

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Disable caching for development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🏛️  Temple Verification Server")
        print(f"=" * 50)
        print(f"✅ Server running at: http://localhost:{PORT}")
        print(f"📂 Serving directory: {os.getcwd()}")
        print(f"\n🌐 Open in browser:")
        print(f"   http://localhost:{PORT}/temple_verification_ui.html")
        print(f"\n📝 Instructions:")
        print(f"   1. Review each temple's data side-by-side")
        print(f"   2. Select the correct HRCE match or 'New Temple'")
        print(f"   3. Add notes for complex cases")
        print(f"   4. Export results when done")
        print(f"\n⌨️  Press Ctrl+C to stop the server")
        print(f"=" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped")
            return

if __name__ == "__main__":
    run_server()
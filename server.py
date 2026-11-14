import http.server
import socketserver
import os
import sys

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class AegisRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Normalize path
        req_path = self.path.split('?')[0].rstrip('/')
        local_dir = os.path.join(DIRECTORY, req_path.lstrip('/'))

        # If a directory is requested without a filename
        if os.path.isdir(local_dir):
            if req_path != "" and not self.path.split('?')[0].endswith('/'):
                # Redirect to include trailing slash
                self.send_response(301)
                new_path = self.path.split('?')[0] + '/'
                if '?' in self.path:
                    new_path += '?' + self.path.split('?')[1]
                self.send_header('Location', new_path)
                self.end_headers()
                return

            # Check if index.html exists
            if os.path.exists(os.path.join(local_dir, 'index.html')):
                return super().do_GET()
            # If code.html exists, serve code.html directly!
            elif os.path.exists(os.path.join(local_dir, 'code.html')):
                self.path = req_path + '/code.html'
                if '?' in self.path:
                    self.path += '?' + self.path.split('?')[1]
                return super().do_GET()

        return super().do_GET()

    def end_headers(self):
        # Enable CORS and disable aggressive caching for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

if __name__ == '__main__':
    # Find free port if 8000 is taken
    import socket
    port = PORT
    for candidate in [8000, 8080, 8888, 3000, 5000]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', candidate)) != 0:
                port = candidate
                break

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('0.0.0.0', port), AegisRequestHandler) as httpd:
        print(f"AEGIS DEFENSE NEXUS Server active at http://localhost:{port}")
        print(f"Serving directory: {DIRECTORY}")
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

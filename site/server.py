import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

os.chdir(DIRECTORY)

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.html': 'text/html',
})

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"ADO Site running at http://127.0.0.1:{PORT}")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()

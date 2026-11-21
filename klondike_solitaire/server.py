"""
server.py - Lightweight Python HTTP Server & JSON API for Klondike Solitaire
CSC200 Data Structures & Algorithms | Mid Term Project
Author: @Muhammad Hamza

Provides REST endpoints for the graphical interface and serves web static files:
  - GET  /api/state
  - POST /api/new_game
  - POST /api/draw
  - POST /api/move_tableau
  - POST /api/foundation
  - POST /api/waste_to_tableau
  - POST /api/foundation_to_tableau
  - POST /api/undo
  - POST /api/redo
  - GET  /api/hint
  - POST /api/auto_complete
"""

import sys
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game import KlondikeGame

# Global game instance for the web session
GAME_SESSION = KlondikeGame(draw_mode=1)
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')


class SolitaireRequestHandler(SimpleHTTPRequestHandler):
    """Handles static web files and REST API requests for Klondike Solitaire."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def _send_json(self, data: Dict[str, Any], status: int = 200) -> None:
        """Sends JSON response with CORS headers."""
        payload = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        """Handles CORS pre-flight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self) -> None:
        """Routes GET requests to API or static files."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/api/state':
            self._send_json(GAME_SESSION.to_dict())
            return
        elif path == '/api/hint':
            self._send_json(GAME_SESSION.get_hint())
            return

        # Default: Serve static files from web/
        super().do_GET()

    def do_POST(self) -> None:
        """Routes POST requests to game operations."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Read JSON body if present
        content_length = int(self.headers.get('Content-Length', 0))
        body = {}
        if content_length > 0:
            try:
                body_bytes = self.rfile.read(content_length)
                body = json.loads(body_bytes.decode('utf-8'))
            except Exception:
                body = {}

        if path == '/api/new_game':
            seed = body.get('seed')
            draw_mode = body.get('draw_mode', 1)
            GAME_SESSION.new_game(seed=seed, draw_mode=draw_mode)
            self._send_json({'ok': True, 'state': GAME_SESSION.to_dict()})
            return

        elif path == '/api/draw':
            res = GAME_SESSION.draw()
            res['state'] = GAME_SESSION.to_dict()
            self._send_json(res)
            return

        elif path == '/api/move_tableau':
            src = body.get('src', 0)
            dst = body.get('dst', 0)
            count = body.get('count', 1)
            res = GAME_SESSION.move_tableau_to_tableau(src, dst, count)
            res['state'] = GAME_SESSION.to_dict()
            self._send_json(res)
            return

        elif path == '/api/foundation':
            source = body.get('source', 'W')
            res = GAME_SESSION.move_to_foundation(source)
            res['state'] = GAME_SESSION.to_dict()
            self._send_json(res)
            return

        elif path == '/api/waste_to_tableau':
            dst = body.get('dst', 0)
            res = GAME_SESSION.move_waste_to_tableau(dst)
            res['state'] = GAME_SESSION.to_dict()
            self._send_json(res)
            return

        elif path == '/api/foundation_to_tableau':
            f_idx = body.get('f_idx', 0)
            t_idx = body.get('t_idx', 0)
            res = GAME_SESSION.move_foundation_to_tableau(f_idx, t_idx)
            res['state'] = GAME_SESSION.to_dict()
            self._send_json(res)
            return

        elif path == '/api/undo':
            res = GAME_SESSION.undo()
            res['state'] = GAME_SESSION.to_dict()
            self._send_json(res)
            return

        elif path == '/api/redo':
            res = GAME_SESSION.redo()
            res['state'] = GAME_SESSION.to_dict()
            self._send_json(res)
            return

        elif path == '/api/auto_complete':
            moves = GAME_SESSION.auto_complete()
            self._send_json({'ok': True, 'moves_made': moves, 'state': GAME_SESSION.to_dict()})
            return

        else:
            self._send_json({'ok': False, 'reason': f'Endpoint not found: {path}'}, status=404)


def start_server(port: int = 8080) -> None:
    """Starts local HTTP server on specified port."""
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, SolitaireRequestHandler)
    print(f"\n===========================================================================")
    print(f" Klondike Solitaire Web Server running at: http://127.0.0.1:{port}")
    print(f" Serving graphical interface from: {WEB_DIR}")
    print(f" Press Ctrl+C to stop the server.")
    print(f"===========================================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web server...")
        httpd.server_close()


if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    start_server(port)

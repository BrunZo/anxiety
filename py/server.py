import http.cookies
import json
import os
import random
from http.server import BaseHTTPRequestHandler, HTTPServer

from db import init_db, insert_anxiety_entry, get_statistics

def _get_random_exercise():
    content_dir = "content"
    
    try:
        files = [f for f in os.listdir(content_dir) if os.path.isfile(os.path.join(content_dir, f))]
        
        if not files:
            return None
        
        random_file = random.choice(files)
        file_path = os.path.join(content_dir, random_file)
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
            
    except Exception as e:
        print(f"Error getting random exercise: {e}")
        return None


class RequestHandler(BaseHTTPRequestHandler):

    def _send_json(self, code, data, cookies={}):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        for key in cookies:
            self.send_header("Set-Cookie", f"{key}={cookies[key]}; Path=/; HttpOnly")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _render_page(self, file):
        try:
            url = "html/" + file + ".html"
            with open(url, "rb") as f:
                content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset: utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        except Exception as e:
            self._send_json(404, {"error": e})

    def _redirect(self, path):
        self.send_response(302)
        self.send_header("Location", path)
        self.end_headers()
        self.wfile.write(b"")

    def _get_cookie(self, cookie_name):
        cookie_header = self.headers.get("Cookie")
        cookies = http.cookies.SimpleCookie(cookie_header)
        return cookies.get(cookie_name)

    def do_GET(self):

        if self.path == "/" or self.path == "/button":
            self._render_page("button")

        if self.path == "/dashboard":
            self._render_page("dashboard")

        if self.path == "/form":
            self._render_page("form")

        if self.path == "/exercise":
            self._render_page("exercise")

        if self.path == "/random_exercise":
            exercise_html = _get_random_exercise()
            if exercise_html:
                self._send_json(200, {"exercise": exercise_html})
            else:
                self._send_json(404, {"error": "No exercises available"})

        elif self.path == "/api/stats":
            stats = get_statistics()
            self._send_json(200, stats)

        else:
            self._send_json(404, {"error": "Página no encontrada"})

    def do_POST(self):

        try:
            content_length = int(self.headers.get("Content-Length"))
            body = self.rfile.read(content_length)
            data = json.loads(body)

        except json.JSONDecodeError:
            self._send_json(400, {"error": "Solicitud inválida"})
            return

        if self.path == "/button":
            self._send_json(200, {"message": "Button clicked"})

        elif self.path == "/form":
            anxiety_type = data.get("type", "")
            description = data.get("description", "")
            entry_id = insert_anxiety_entry(anxiety_type, description)
            print(f"Saved anxiety entry (ID: {entry_id}): type={anxiety_type}, description={description}")
            self._send_json(200, {"message": "Form submitted", "data": data})

        else:
            self._send_json(404, {"error": "Página no encontrada"})
        
if __name__ == "__main__":
    init_db()
    print("Database initialized")
    
    server = HTTPServer(("0.0.0.0", 8000), RequestHandler)
    print("Server starting on http://0.0.0.0:8000")
    server.serve_forever()

import json
import re
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


@dataclass
class Category:
    id: int
    name: str


@dataclass
class Service:
    id: int
    name: str
    category_id: int


categories = [
    Category(1, "Стрижки и укладки"),
    Category(2, "Борода и усы"),
    Category(3, "Уход за волосами"),
]

services = [
    Service(1, "Мужская стрижка", 1),
    Service(2, "Женская стрижка", 1),
    Service(3, "Детская стрижка", 1),
    Service(4, "Укладка", 1),
    Service(5, "Стрижка машинкой", 1),
    Service(6, "Моделирование бороды", 2),
    Service(7, "Стрижка усов", 2),
]


def get_category(category_id: int) -> dict | None:
    category = next((item for item in categories if item.id == category_id), None)
    if category is None:
        return None

    return {
        "id": category.id,
        "name": category.name,
        "servicesCount": sum(service.category_id == category_id for service in services),
    }


class RequestHandler(BaseHTTPRequestHandler):
    def send_body(self, status: int, body: str, content_type: str) -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        match = re.fullmatch(r"/categories/(-?[0-9]+)/?", path)
        if match is None:
            self.send_body(404, "Not found", "text/plain")
            return

        category = get_category(int(match.group(1)))
        if category is None:
            self.send_body(404, "Category not found", "text/plain")
            return

        self.send_body(200, json.dumps(category, ensure_ascii=False), "application/json")


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 8000), RequestHandler) as server:
        print("http://127.0.0.1:8000/categories/1")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

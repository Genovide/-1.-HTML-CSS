import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine, init_db
from models import Master


def serialize_master(master: Master) -> dict:
    return {
        "id": master.id,
        "name": master.name,
        "specialization": master.specialization,
    }


def get_masters(specialization: str | None = None) -> list[dict]:
    statement = select(Master).order_by(Master.id)
    if specialization is not None:
        statement = statement.where(Master.specialization == specialization)

    with Session(engine) as session:
        return [serialize_master(master) for master in session.scalars(statement)]


def get_master(master_id: int) -> dict | None:
    with Session(engine) as session:
        master = session.get(Master, master_id)
        return serialize_master(master) if master is not None else None


class RequestHandler(BaseHTTPRequestHandler):
    def send_json(self, status: int, data: object) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        url = urlsplit(self.path)
        if url.path.rstrip("/") == "/masters":
            query = parse_qs(url.query, keep_blank_values=True)
            specialization = query.get("specialization", [None])[0]
            self.send_json(200, get_masters(specialization))
            return

        match = re.fullmatch(r"/masters/(-?[0-9]+)/?", url.path)
        if match is None:
            self.send_json(404, {"detail": "Not Found"})
            return

        try:
            master_id = int(match.group(1))
        except ValueError:
            self.send_json(404, {"detail": "Master not found"})
            return

        if not 0 < master_id <= 9223372036854775807:
            self.send_json(404, {"detail": "Master not found"})
            return

        master = get_master(master_id)
        if master is None:
            self.send_json(404, {"detail": "Master not found"})
            return

        self.send_json(200, master)


if __name__ == "__main__":
    init_db()
    with ThreadingHTTPServer(("127.0.0.1", 8000), RequestHandler) as server:
        print("http://127.0.0.1:8000/masters")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

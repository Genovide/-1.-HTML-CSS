import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import engine, init_db
from models import Category, Master, Service
from schemas import ServiceCreate


def serialize_master(master: Master) -> dict:
    return {
        "id": master.id,
        "name": master.name,
        "specialization": master.specialization,
    }


def serialize_service(service: Service) -> dict:
    return {
        "id": service.id,
        "categoryId": service.category_id,
        "title": service.title,
        "desc": service.desc,
        "duration": service.duration,
        "price": service.price,
    }


def get_masters(specialization: str | None = None) -> list[dict]:
    statement = select(Master).order_by(Master.id)
    if specialization is not None:
        statement = statement.where(Master.specialization == specialization)

    with Session(engine) as session:
        return [serialize_master(master) for master in session.scalars(statement)]


class RequestHandler(BaseHTTPRequestHandler):
    def send_json(self, status: int, data: object) -> None:
        body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        url = urlsplit(self.path)
        if url.path.rstrip("/") == "/masters":
            query = parse_qs(url.query, keep_blank_values=True)
            self.send_json(200, get_masters(query.get("specialization", [None])[0]))
            return

        if url.path.rstrip("/") == "/services":
            with Session(engine) as session:
                services = session.scalars(select(Service).order_by(Service.id))
                self.send_json(200, [serialize_service(service) for service in services])
            return

        match = re.fullmatch(r"/(masters|categories)/([0-9]+)/?", url.path)
        if match is None:
            self.send_json(404, {"detail": "Not Found"})
            return

        kind, raw_id = match.groups()
        try:
            item_id = int(raw_id)
        except ValueError:
            item_id = 0
        if not 0 < item_id <= 9223372036854775807:
            self.send_json(404, {"detail": "Not Found"})
            return

        with Session(engine) as session:
            if kind == "masters":
                master = session.get(Master, item_id)
                if master is None:
                    self.send_json(404, {"detail": "Master not found"})
                else:
                    self.send_json(200, serialize_master(master))
                return

            category = session.get(Category, item_id)
            if category is None:
                self.send_json(404, {"detail": "Category not found"})
                return
            count = session.scalar(
                select(func.count()).select_from(Service).where(Service.category_id == item_id)
            )
            self.send_json(200, {
                "id": category.id,
                "name": category.name,
                "servicesCount": count,
            })

    def do_POST(self) -> None:
        if urlsplit(self.path).path.rstrip("/") != "/services":
            self.send_json(404, {"detail": "Not Found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"detail": "Invalid Content-Length"})
            return
        if length < 0 or length > 1000000:
            self.send_json(413, {"detail": "Request body too large"})
            return

        try:
            data = ServiceCreate.model_validate_json(self.rfile.read(length))
        except ValidationError as error:
            details = json.loads(error.json(include_url=False, include_input=False))
            self.send_json(422, {"detail": details})
            return

        with Session(engine) as session:
            if session.get(Category, data.categoryId) is None:
                self.send_json(404, {"detail": "Category not found"})
                return

            service = Service(
                category_id=data.categoryId,
                title=data.title,
                desc=data.desc,
                duration=data.duration,
                price=data.price,
            )
            session.add(service)
            session.commit()
            session.refresh(service)
            self.send_json(201, serialize_service(service))


if __name__ == "__main__":
    init_db()
    with ThreadingHTTPServer(("127.0.0.1", 8000), RequestHandler) as server:
        print("http://127.0.0.1:8000/services")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

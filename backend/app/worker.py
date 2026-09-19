from __future__ import annotations

from redis import Redis
from rq import Queue, Worker

from app.config import get_settings
from app.db import init_db


def main() -> None:
    settings = get_settings()
    init_db()
    connection = Redis.from_url(settings.redis_url)
    queue = Queue("research", connection=connection)
    worker = Worker([queue], connection=connection)
    worker.work(with_scheduler=False)


if __name__ == "__main__":
    main()

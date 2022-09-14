import asyncio
import argparse

from aiohttp import web
from app.api import routes
from app.context import AppContext


async def create_app():
    app = web.Application()

    # TODO: web.client_max_size = 63 - По умолчанию aiohttp принимает 2мб макс, надо 63
    ctx = AppContext(secrets_dir='secrets')  # Контекст - это всё зависимости

    app.on_startup.append(ctx.on_startup)  # То, что мы сделаем на старте приложения
    app.on_shutdown.append(ctx.on_shutdown)  # То, что мы сделаем при завершении работы

    routes.setup_routes(app, ctx)  # Чтобы не перечислять все ручки

    return app


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--secrets-dir', type=str, required=True)

    return parser.parse_args()


def main():
    # args = parse_args()

    app = asyncio.get_event_loop().run_until_complete(create_app())

    web.run_app(app)


if __name__ == '__main__':
    main()

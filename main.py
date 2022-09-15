import asyncio
import argparse

from aiohttp import web
from app.api import routes
from app.context import AppContext


async def create_app():
    app = web.Application()

    ctx = AppContext(secrets_dir='secrets')

    app.on_startup.append(ctx.on_startup)
    app.on_shutdown.append(ctx.on_shutdown)

    routes.setup_routes(app, ctx)

    return app


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--secrets-dir', type=str, required=True)

    return parser.parse_args()


def main():
    app = asyncio.get_event_loop().run_until_complete(create_app())
    web.run_app(app, port=80)


if __name__ == '__main__':
    main()

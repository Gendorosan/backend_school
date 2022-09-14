from aiohttp import web

from app.api import handles
from app.context import AppContext


# Нужно для того чтобы сразу принимать и запрос и контекст
def wrap_handler(handler, context):
    async def wrapper(request):
        return await handler(request, context)

    return wrapper


# app: передаем наше приложение #ctx: передаем наш контекст
def setup_routes(app: web.Application, ctx: AppContext) -> None:
    app.router.add_post(
        '/imports',
        wrap_handler(
            handles.import_handle,
            ctx,
        ),
    )
    app.router.add_delete(
        r'/delete/{data}',
        wrap_handler(
            handles.delete_handle,
            ctx,
        ),
    )
    app.router.add_get(
        r'/nodes/{data}',
        wrap_handler(
            handles.get_nodes_handle,
            ctx,
        ),
    )
    app.router.add_get(
        r'/updates',
        wrap_handler(
            handles.get_updates_handle,
            ctx,
        ),
    )
    app.router.add_get(
        r'/node/{id}/history',
        wrap_handler(
            handles.get_node_history_handle,
            ctx,
        ),
    )




from aiohttp import web

from app.context import AppContext
import app.api.validation_check as check
from app import database as dbo


async def post_request_content(request: web.Request):
    text = await request.json()
    return text


async def import_handle(request: web.Request, context: AppContext) -> web.Response:
    try:
        data = await post_request_content(request)

        if check.check_json(data):
            if await dbo.import_items(context, data):
                return web.json_response(
                    {
                        "code": 200,
                        "message": "Import was successful"
                    },
                    status=200
                )

        return web.json_response(
            {
                "code": 400,
                "message": "Validation Failed"
            },
            status=400
        )

    except SyntaxError:
        return web.json_response(
            {
                "code": 400,
                "message": "Validation Failed"
            },
            status=400
        )


async def delete_handle(request: web.Request, context: AppContext) -> web.Response:
    try:
        data = request.match_info['data']

        date = request.rel_url.query['date']

        if check.check_item_id(data) and check.datetime_valid(date):
            if await dbo.already_in_the_database(context, data):
                if await dbo.delete_element(context, data, date):
                    return web.json_response(
                        {
                            "code": 200,
                            "message": "The data was successfully deleted"
                        },
                        status=200
                    )
            else:
                return web.json_response(
                    {
                        "code": 404,
                        "message": "File not found"
                    },
                    status=404
                )

        else:
            return web.json_response(
                {
                    "code": 400,
                    "message": "Validation Failed"
                },
                status=400
            )
    except SyntaxError:
        return web.json_response(
            {
                "code": 400,
                "message": "Validation Failed"
            },
            status=400
        )


async def get_nodes_handle(request: web.Request, context: AppContext) -> web.Response:
    try:
        data = request.match_info['data']
        if check.check_item_id(data):
            if await dbo.already_in_the_database(context, data):
                print('already_in_the_database')
                return web.json_response(
                    await dbo.get_nodes(context, data)
                )

            else:
                return web.json_response(
                    {
                        "code": 404,
                        "message": "File not found"
                    },
                    status=404
                )

        else:
            return web.json_response(
                {
                    "code": 400,
                    "message": "Validation Failed"
                },
                status=400
            )
    except SyntaxError:
        return web.json_response(
            {
                "code": 400,
                "message": "Validation Failed"
            },
            status=400
        )


async def get_updates_handle(request: web.Request, context: AppContext) -> web.Response:
    try:

        date = request.rel_url.query['date']

        if check.datetime_valid(date):
            return web.json_response(await dbo.get_items_updated_in_last_day(context, date))
        else:
            return web.json_response(
                {
                    "code": 400,
                    "message": "Validation Failed"
                },
                status=400
            )

    except SyntaxError:
        return web.json_response(
            {
                "code": 400,
                "message": "Validation Failed"
            },
            status=400
        )


async def get_node_history_handle(request: web.Request, context: AppContext) -> web.Response:
    try:

        item_id = request.match_info['id']
        date_start = request.rel_url.query['dateStart']
        date_end = request.rel_url.query['dateEnd']

        if check.datetime_valid(date_start) and check.datetime_valid(date_end):
            return web.json_response(await dbo.get_item_history(context, item_id, date_start, date_end))
        else:
            return web.json_response(
                {
                    "code": 400,
                    "message": "Validation Failed"
                },
                status=400
            )

    except SyntaxError:
        return web.json_response(
            {
                "code": 400,
                "message": "Validation Failed"
            },
            status=400
        )

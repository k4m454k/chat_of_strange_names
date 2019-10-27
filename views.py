import logging

import aiohttp
import aiohttp_jinja2
from aiohttp import web
from faker import Faker
from names import get_name

log = logging.getLogger(__name__)


def get_random_name():
    fake = Faker(locale='RU_ru')
    return fake.name()


async def index(request):
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})

    await ws_current.prepare(request)

    name = get_name()
    log.info('%s joined.', name)

    await ws_current.send_json({'action': 'connect', 'name': name, 'peoples': len(request.app['websockets'].values()) + 1})

    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'join', 'name': name, 'peoples': len(request.app['websockets'].values())+1})
    request.app['websockets'][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == aiohttp.WSMsgType.text:
            for ws in request.app['websockets'].values():
                if ws is not ws_current:
                    await ws.send_json(
                        {'action': 'sent', 'name': name, 'text': msg.data, 'peoples': len(request.app['websockets'].values())})
        else:
            break

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name, 'peoples': len(request.app['websockets'].values())})

    return ws_current

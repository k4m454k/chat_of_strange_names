import logging

import aiohttp
import aiohttp_jinja2
from aiohttp import web
from names import get_name
import asyncio
import re
from settings import service_password, max_message_symbols
from antispam import Antispam, User

log = logging.getLogger(__name__)

asp = Antispam()

def clean_html(raw_html):
    cleanr = re.compile(r'<.*?>')
    clean_text = re.sub(cleanr, '', raw_html)
    return clean_text


async def index(request):
    if asp.is_banned(request.remote):
        return aiohttp_jinja2.render_template('ban.html', request, {})
    user = User(request.remote)
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})

    await ws_current.prepare(request)
    name = get_name(available_names=request.app['websockets'].keys())
    log.info('%s joined.', name)

    await ws_current.send_json({'action': 'connect', 'name': name, 'peoples': len(request.app['websockets'].values()) + 1})

    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'join', 'name': name, 'peoples': len(request.app['websockets'].values())+1})
    request.app['websockets'][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == aiohttp.WSMsgType.text:
            if msg.data.startswith("/"):
                if not msg.data.startswith("/service"+service_password):
                    await ws_current.send_json(
                        {'action': 'service',
                         'header': "Service password",
                         'text': f"Service password wrong"
                         }
                    )
                    continue
                message = msg.data[len("/service"+service_password):]
                print(message)
                for ws in request.app['websockets'].values():
                    await ws.send_json(
                        {'action': 'service', 'header': "Service message", 'text': message}
                    )
                continue

            if len(msg.data) > max_message_symbols:
                await ws_current.send_json(
                    {'action': 'service',
                     'header': "Service message",
                     'text': f"Very long message, {max_message_symbols} symbols max. Kick"
                     }
                )
                break

            identic_massages = user.message(msg.data)

            if 7 > identic_massages > 5:
                await ws_current.send_json(
                    {'action': 'service',
                     'header': "Стоп Спам",
                     'text': f"Если вы продолжите спамить, вы будете забанены в чате."
                     }
                )
            elif identic_massages > 7:
                asp.ban(request.remote)
                await ws_current.send_json(
                    {'action': 'service',
                     'header': "Вы забанены",
                     'text': "К сожалению вы пренебрегли правилом не спамить в чате и отныне забанены. <hr> Бан не вечный и вам придётся немного подождать. В будущем воздержитесь от спама и сделайте своё пребывание в чате веселым и не напряжным для остальных участников общения."
                     }
                )
                break
            for ws in request.app['websockets'].values():
                if ws is not ws_current:
                    await ws.send_json(
                        {'action': 'sent', 'name': name, 'text': clean_html(msg.data), 'peoples': len(request.app['websockets'].values())})
        else:
            break

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name, 'peoples': len(request.app['websockets'].values())})

    return ws_current

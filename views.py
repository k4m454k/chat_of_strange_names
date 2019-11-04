import logging

import aiohttp
import aiohttp_jinja2
from aiohttp import web
from names import get_name, get_random_name
import asyncio
import re
import uuid
from PIL import Image
import os
from settings import service_password, max_message_symbols
from antispam import Antispam, User

log = logging.getLogger(__name__)

asp = Antispam()


def clean_html(raw_html):
    cleanr = re.compile(r'<.*?>')
    clean_text = re.sub(cleanr, '', raw_html)
    return clean_text


async def send_service(ws, text, header="Сервисное сообщение"):
    await ws.send_json(
        {'action': 'service',
         'header': header,
         'text': text
         }
    )


async def index(request):
    if asp.is_banned(request.remote):
        log.info(f"Banned ip {request.remote} request chat")
        return aiohttp_jinja2.render_template('ban.html', request, {})
    user = User(request.remote)
    ws_current = web.WebSocketResponse()
    ws_ready = ws_current.can_prepare(request)
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})

    await ws_current.prepare(request)
    name = get_name(available_names=request.app['websockets'].keys())
    log.info(f'{name} joined.')

    await ws_current.send_json({
        'action': 'connect',
        'name': name,
        'peoples': len(request.app['websockets'].values()) + 1,
        'inchat': list(request.app['websockets'].keys())
    })

    for ws in request.app['websockets'].values():
        await ws.send_json({
            'action': 'join',
            'name': name,
            'peoples': len(request.app['websockets'].values())+1,
            'inchat': list(request.app['websockets'].keys())
        })
    request.app['websockets'][name] = ws_current

    while True:
        msg = await ws_current.receive()

        if msg.type == aiohttp.WSMsgType.binary:
            print(msg.data)

        if msg.type == aiohttp.WSMsgType.text:
            if msg.data.startswith("/"):
                log.info(f"Recieved / symbol from {name}. Requested: {msg.data}")
                if not msg.data.startswith("/service"+service_password):
                    await send_service(ws_current, f"Пароль неверен")
                    user.passwod_attemps += 1
                    if user.passwod_attemps > 3:
                        await send_service(
                            ws_current,
                            "К сожалению вы пытались подобрать сервисный пароль и отныне забанены. <hr> Бан не "
                            "вечный и вам придётся немного подождать. В будущем воздержитесь от перебора паролей и "
                            "сделайте своё пребывание в чате веселым и не напряжным для остальных участников общения.",
                            header='Вы забанены'
                        )
                        asp.ban(request.remote)
                        log.info(f"User {name}:{request.remote} baned!")
                        break
                    continue
                message = msg.data[len("/service"+service_password):]
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
                log.info(f"User {name}:{request.remote} recieve ban warning")
                await ws_current.send_json(
                    {'action': 'service',
                     'header': "Стоп Спам",
                     'text': f"Если вы продолжите спамить, вы будете забанены в чате."
                     }
                )
            elif identic_massages > 7:
                asp.ban(request.remote)
                log.info(f"User {name}:{request.remote} baned!")
                await ws_current.send_json(
                    {'action': 'service',
                     'header': "Вы забанены",
                     'text': "К сожалению вы пренебрегли правилом не спамить в чате и отныне забанены. <hr> Бан не "
                             "вечный и вам придётся немного подождать. В будущем воздержитесь от спама и сделайте "
                             "своё пребывание в чате веселым и не напряжным для остальных участников общения. "
                     }
                )
                break
            for ws in request.app['websockets'].values():
                if ws is not ws_current:
                    await ws.send_json({
                        'action': 'sent',
                        'name': name,
                        'text': replace_name_to_span(clean_html(msg.data), list(request.app['websockets'].keys())),
                        'peoples': len(request.app['websockets'].values()),
                        'inchat': list(request.app['websockets'].keys())
                    })

        else:
            break

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name, 'peoples': len(request.app['websockets'].values()),
                        'inchat': list(request.app['websockets'].keys())})

    return ws_current


def replace_name_to_span(message, names_list):
    for name in names_list:
        message = message.replace(name, f'<span class="badge badge-primary">{name}</span>')
    return message


async def image(request):
    imgname = request.match_info.get('imgname')
    log.info(f"Request image {imgname}.jpg")
    return web.FileResponse(f'./images/{imgname}.jpg')


async def post_image(request):
    reader = await request.multipart()
    image = await reader.next()
    filename = image.filename
    new_filename = str(uuid.uuid4())
    log.info(f"Upload file {filename} to {new_filename}")
    size = 0
    with open(os.path.join('images', new_filename + ".jpg"), 'wb') as f:
        while True:
            chunk = await image.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)
    return web.json_response({"file_uploaded": new_filename})

import asyncio
import selectors
import sys
from datetime import datetime
from enum import Enum

selector = selectors.DefaultSelector()


class ChangeType(Enum):
    ADD = 'Добавлен'
    DELETE = 'Удален'
    UPDATE = 'Изменен'


async def start_server(ip_: str, port: int):
    server = await asyncio.start_server(
        recv_send_message, ip_, port)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


async def recv_send_message(reader, writer):
    change_type = ChangeType
    data = await reader.read(255)
    changes = data.decode().split(';')
    print('{}: Файл {} размером {} байт, был {}'.format(
        datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        changes[0],
        changes[1],
        change_type[changes[2]].value.lower()
    ))

    writer.write(data)
    await writer.drain()
    writer.close()


if __name__ == '__main__':
    args = sys.argv
    args.pop(0)
    port = 3000

    if '-ip' not in args:
        print("argument ip is required")
        exit(1)
    if '-p' in args:
        port = int(args[args.index('-p') + 1])

    ip = args[args.index('-ip') + 1]

    asyncio.run(start_server(ip, port))

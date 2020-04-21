import socket
import sys
from enum import Enum
from datetime import datetime
import selectors

selector = selectors.DefaultSelector()


class ChangeType(Enum):
    ADD = 'Добавлен'
    DELETE = 'Удален'
    UPDATE = 'Изменен'


def init_server(ip: str, port: int):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    server_socket.bind(server_address)
    server_socket.listen(1)

    selector.register(fileobj=server_socket, events=selectors.EVENT_READ, data=accept_connection)


def accept_connection(server_socket):
    # Wait for a connection
    client_socket, client_address = server_socket.accept()
    print('Connection from: %s:%s' % client_address)

    selector.register(fileobj=client_socket, events=selectors.EVENT_READ, data=recv_send_message)


def recv_send_message(client_socket):
    change_type = ChangeType
    try:
        request = client_socket.recv(256)
        if request:
            changes = request.decode().split(';')
            print('{}: Файл {} размером {} байт, был {}'.format(
                datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                changes[0],
                changes[1],
                change_type[changes[2]].value.lower()
            ))
            client_socket.send('Success\n'.encode())
        else:
            selector.unregister(client_socket)
            client_socket.close()

    finally:
        selector.unregister(client_socket)
        client_socket.close()


def manager():
    while True:
        events = selector.select()

        for key, _ in events:
            callback = key.data
            callback(key.fileobj)


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

    init_server(ip, port)
    manager()

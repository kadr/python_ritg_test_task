import os
import sys
import socket
from time import sleep

args = sys.argv
args.pop(0)
port = 10000

SCAN_TIMEOUT_IN_SEC = 2

if '-folder' not in args:
    print("argument folder is required")
    exit(1)
if '-ip' not in args:
    print("argument ip is required")
    exit(1)
if '-p' in args:
    port = int(args[args.index('-p') + 1])

folder = args[args.index('-folder') + 1]
ip = args[args.index('-ip') + 1]


def send_changes(path: str, size: float, change_type: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    print('Connecting to %s:%s' % server_address)
    sock.connect(server_address)
    try:
        message = ';'.join([path, str(size), change_type])
        sock.send(message.encode())

        print(sock.recv(256).decode())

    finally:
        sock.close()


files_dict = {}

while True:
    entries = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            size = os.path.getsize(path)
            entries[path] = size
            if path not in files_dict:
                send_changes(path, size, 'ADD')
            if path in files_dict and files_dict[path] != size:
                send_changes(path, size, 'UPDATE')
    if len(files_dict) > len(entries):
        items = set(files_dict.items()) - set(entries.items())
        for item in items:
            send_changes(item[0], float(item[1]), 'DELETE')
    if files_dict != entries and len(files_dict) == len(entries):
        # Проверка на переименование файла. Словари не равны содержимым, но количество записей в них
        # одиноково,а в этом случае надо старый файл пометить как удаленный,
        # так как переименование состоит из 2 операций, удалить старый и добавить новый
        old_items = set(files_dict.items()) - set(entries.items())
        new_items = set(entries.items()) - set(files_dict.items())
        # index = 0
        for path, size in new_items:
            old_path, old_size = old_items.pop()
            if path != old_path and size == old_size:
                # Помечаем как удаленный, так как выше мы уже пометили переименованный файл, как новый
                send_changes(old_path, old_size,  'DELETE')

    files_dict = entries
    sleep(SCAN_TIMEOUT_IN_SEC)

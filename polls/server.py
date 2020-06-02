# данные сервера
from socket import *


def run():
    addr = ('localhost', 7777)
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# bind - связывает адрес и порт с сокетом
    tcp_socket.bind(addr)
# listen - запускает прием TCP
    tcp_socket.listen(1)

# Бесконечный цикл работы программы
    while True:
        # getLastFromDb()
        conn, addr = tcp_socket.accept()
        print('client addr: ', addr)


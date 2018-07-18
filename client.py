import socket
from threading import Thread

from type_msg import *
from jim import f_encode, f_decode


class CClient:
    def __init__(self, name):
        self.name = name

    def send_msg(self, serv_sock):
        while True:
            to = 'Fox'  # input('Кому: ')
            msg = f_msg(to, self.name, input('Текст: '))
            bj_msg = f_encode(msg)
            serv_sock.send(bj_msg)

    def tr_send(self, serv_sock):
        t = Thread(target=self.send_msg, args=serv_sock)
        t.start()

    def recv_msg(self, serv_sock):
        bj_msg = serv_sock.recv(1024)
        msg = f_decode(bj_msg)
        for name, text in msg.items():
            print('От{}: {}'.format(name, text))

    @staticmethod
    def meeting(serv_sock):
        msg = f_presence('Alex')
        jmsg = json.dumps(msg)
        bj_msg = jmsg.encode()
        serv_sock.send(bj_msg)


if __name__ == '__main__':
    with socket.socket() as sock:
        sock.connect(('127.0.0.1', 7777))
        cli = CClient('Alex')
        cli.meeting(sock)
        cli.tr_send(sock)
        while True:
            cli.recv_msg(sock)

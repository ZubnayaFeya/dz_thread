import socket, json
from queue import Queue
from threading import Thread

from jim import f_encode, f_decode

class CServer:
    def __init__(self):
        self.addr = '127.0.0.1'
        self.port = 7777
        self.in_msg = Queue()    # обычная очередь сообщений
        self.conn_msg = Queue()  # сообщения до авторизации
        self.out_msg = Queue()   # сообщения для отправки
        self.clients = {}        # авторизованные клиенты
        self.cl_non_auth = []    # не авторизованные клиенты

    def create_sock(self):
        sock = socket.socket()
        sock.bind((self.addr, self.port))
        sock.listen(15)
        sock.settimeout(0.2)
        return sock

    def disconnect_cl(self, sock_cl, addr):
        sock_cl.close()
        print('{} не прислал корректный пресенс и был отключен'.format(addr))

    def recv_conn(self, sock_cl, addr):
        sock_cl.settimeout(0.5)
        try:
            data = sock_cl.recv(1024)
        except socket.timeout:
            self.disconnect_cl(sock_cl, addr)
            return None
        else:
            msg = f_decode(data)
            return msg

    def meeting(self, sock_cl, addr):
        msg = self.recv_conn(sock_cl, addr)
        if msg is not None:
            if msg['action'] == 'presence':
                self.clients[msg['user']['account_name']] = sock_cl
                print('{} успешно подключился'.format(msg['user']['account_name']))
            else:
                self.disconnect_cl(sock_cl, addr)

    def recv_msg(self):
        while True:
            for sock_cl in self.clients.values():
                sock_cl.settimeout(0.2)
                try:
                    data = sock_cl.recv(1024)
                except socket.timeout:
                    pass
                else:
                    msg = f_decode(data)
                    self.in_msg.put(msg)

    def prep_responce(self):
        msg = self.in_msg.get()
        if msg['to'] in self.clients:
            sock_out = self.clients[msg['to']]
            self.out_msg.put({sock_out: msg})

    def send_msg(self):
        while True:
            data = self.out_msg.get()
            sock_cl, msg = data.popitem()
            bj_data = f_encode(msg)
            sock_cl.send(bj_data)

    def loop_connect(self, sock_serv):
        while True:
            try:
                conn, addr = sock_serv.accept()
            except socket.timeout:
                pass
            else:
                self.meeting(conn, addr)


if __name__ == '__main__':
    srv = CServer()
    sock_s = srv.create_sock()

    thr_recv = Thread(target=srv.recv_msg, daemon=True)
    thr_recv.start()

    thr_conn = Thread(target=srv.loop_connect, args=(sock_s,), daemon=True)
    thr_conn.start()

    thr_send = Thread(target=srv.send_msg, daemon=True)
    thr_send.start()

    while True:
        srv.prep_responce()

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
        self.clients = {}
        self.cl_non_auth = []

    def create_sock(self):
        sock = socket.socket()
        sock.bind((self.addr, self.port))
        sock.listen(15)
        sock.settimeout(0.2)
        return sock

    def recv_conn(self):
        while True:
            for sock_cl in self.cl_non_auth:
                data = sock_cl.recv(1024)
                msg = f_decode(data)
                self.conn_msg.put({sock_cl: msg})

    def recv_msg(self):
        while True:
            for sock_cl in self.clients.values():
                data = sock_cl.recv(1024)
                msg = f_decode(data)
                self.in_msg.put({sock_cl: msg})

    def tr_conn_recv(self):
        t = Thread(target=self.recv_conn)
        t.start()

    def tr_recv(self):
        t = Thread(target=self.recv_msg)
        t.start()

    def prep_con_resp(self):
        dict_data = self.conn_msg.get()
        for sock_from, msg in dict_data:
            if msg['action'] == 'presence':
                self.clients[msg['name']] = sock_from

    def prep_responce(self):
        dict_data = self.in_msg.get()
        for sock_from, msg in dict_data:
            if msg['in'] in self.clients:
                sock_out = self.clients[msg['in']]
                self.out_msg.put({sock_out: msg})

    def send_msg(self, sock):
        while True:
            data = self.out_msg.get()
            j_data = json.dumps(data)
            byte_data = j_data.encode()
            sock.send(byte_data)

    def loop_connect(self, sock_serv):
        while True:
            try:
                addr, conn = sock_serv.accept()
                self.cl_non_auth.append(conn)
            except socket.timeout:
                pass
            finally:
                self.prep_con_resp()
                self.prep_responce()


if __name__ == '__main__':
    srv = CServer()
    sock_s = srv.create_sock()
    srv.tr_conn_recv()
    srv.tr_recv()
    while True:
        srv.loop_connect(sock_s)


import socket
import select

from .message_types import HEADER_SIZE, MESSAGE_SIZE, ACK, DELIMETER, PADDING, VALID_TYPES, MessageSizeException, MessageTypeException

# SERVER_IP = "192.168.137.1"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 60006


class ClientDisconnectException(Exception):
    pass


class Server:

    def __init__(self, server_port=SERVER_PORT) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", server_port))
        self.sock.listen(5)

    def connect(self):
        self.conn, self.addr = self.sock.accept()

    def send_ack(self):
        data = str(ACK + DELIMETER + PADDING *
                   (MESSAGE_SIZE)).encode("ascii")
        self.conn.sendall(data)

    def send_message(self, msg_type: str, msg: str):
        data = msg.encode("ascii")
        if not msg_type in VALID_TYPES:
            raise MessageTypeException
        if len(data) > MESSAGE_SIZE:
            raise MessageSizeException
        data = (msg_type + DELIMETER).encode("ascii") + data + \
            (PADDING * (MESSAGE_SIZE - len(data))).encode("ascii")
        print(data)
        self.sock.sendall(data)

    def read_messages(self, timeout: float = 0.1) -> "list[tuple[str, str]]":
        messages: "list[tuple[str, str]]" = []
        while True:
            read_list, write_list, error_list = select.select(
                [self.conn], [], [], timeout)
            if read_list:
                print("reading...", read_list)
                buffer: str = self.conn.recv(HEADER_SIZE + MESSAGE_SIZE).decode("ascii")
                if buffer == '':
                    raise ClientDisconnectException
                end_padding_idx = buffer.find(PADDING, 7)
                if end_padding_idx == -1:
                    messages.append((buffer[0:6], buffer[7:]))
                else:
                    messages.append((buffer[0:6], buffer[7:end_padding_idx]))
            else:
                break
        return messages


if __name__ == "__main__":
    s = Server()
    s.connect()
    print(s.conn)

    from message_types import STATE_CHANGE
    from time import sleep
    while True:
        msgs = s.read_messages()
        if msgs:
            for msg in msgs:
                print(msg)
                if msg[0] == STATE_CHANGE:
                    s.send_ack()

        else:
            print("no messages")
        sleep(0.3)

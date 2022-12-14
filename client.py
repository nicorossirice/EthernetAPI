import select
import socket

from .message_types import ACK, GPS_LOC, STATE_CHANGE, HEADING, HEARTBEAT, DELIMETER, PADDING, HEADER_SIZE, MESSAGE_SIZE, VALID_TYPES, MessageTypeException, MessageSizeException

class Client:

    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pend_ack = False

    def connect(self, server_ip, server_port) -> bool:
        try:
            self.sock.connect((server_ip, server_port))
            return True
        except ConnectionError:
            return False
        except TimeoutError:
            return False

    def send_gps_loc(self, message: str):
        data = message.encode("ascii")
        if len(data) > MESSAGE_SIZE:
            raise MessageSizeException
        data = (GPS_LOC + DELIMETER).encode("ascii") + data + \
            (PADDING * (MESSAGE_SIZE - len(data))).encode("ascii")
        print(data)
        self.sock.sendall(data)
        self.pend_ack = True

    def send_state_change(self, message: str):
        data = message.encode("ascii")
        if len(data) > MESSAGE_SIZE:
            raise MessageSizeException
        data = (STATE_CHANGE + DELIMETER).encode("ascii") + data + \
            (PADDING * (MESSAGE_SIZE - len(data))).encode("ascii")
        self.sock.sendall(data)
        self.pend_ack = True

    def send_heading(self, message: str):
        data = message.encode("ascii")
        if len(data) > MESSAGE_SIZE:
            raise MessageSizeException
        data = (HEADING + DELIMETER).encode("ascii") + data + \
            (PADDING * (MESSAGE_SIZE - len(data))).encode("ascii")
        self.sock.sendall(data)
        self.pend_ack = True

    def send_heartbeat(self):
        data = str(HEARTBEAT + DELIMETER + PADDING *
                   (MESSAGE_SIZE)).encode("ascii")
        print(data)
        self.sock.sendall(data)

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

    def read_messages(self, timeout: float = 0.1, max_messages: int = 10) -> "list[tuple[str, str]]":
        messages: "list[tuple[str, str]]" = []
        while True:
            read_list, write_list, error_list = select.select(
                [self.sock], [], [], timeout)
            if read_list:
                buffer: str = self.sock.recv(HEADER_SIZE + MESSAGE_SIZE).decode("ascii")
                end_padding_idx = buffer.find(PADDING, 7)
                if end_padding_idx == -1:
                    messages.append((buffer[0:6], buffer[7:]))
                else:
                    messages.append((buffer[0:6], buffer[7:end_padding_idx]))
                if messages[-1][0] == ACK:
                    self.pend_ack = False
                if len(messages) > max_messages:
                    break
            else:
                break
        return messages

    def disconnect(self):
        self.sock.close()


if __name__ == "__main__":
    c = Client()
    c.connect()

    from time import sleep
    sleep(2)

    c.send_heartbeat()

    sleep(2)

    c.send_gps_loc("some garbage")

    sleep(2)

    c.send_state_change("more garbage")

    sleep(2)

    print(c.read_messages())

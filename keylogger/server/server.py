import socket
from datetime import datetime

def run():
    print(f"Server started at:{datetime.now()}")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('192.168.1.28', 12345))
    s.listen(1)
    conn, addr = s.accept()

    while 1:
        data = conn.recv(1024)
        if not data:
            break
        
        print(f"Received:{data.decode()}")

    conn.close()

    print(f"Server closed at:{datetime.now()}")

run()
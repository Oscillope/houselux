from disp import Display
from buttons import Buttons
import network
import socket
from utime import sleep
import hue

is_on = False

sta_if = network.WLAN(network.STA_IF)

screen = Display(5)
screen.print("Hello!")
screen.softbtn(["Off", "Conn..."])

def btn_cb():
    global screen
    global is_on
    global sta_if
    global hue_br
    if not sta_if.isconnected():
        print("Tried to change state before connected")
        return
    screen.softbtn(["", "Wait"])
    for client in config["clients"]:
        addr_info = socket.getaddrinfo(client, 4444)
        addr = addr_info[0][-1]
        sock = socket.socket()
        sock.connect(addr)
        if is_on:
            sock.send("0")
        else:
            sock.send("1")
        sock.send("\r\n")
        while True:
            resp = sock.recv(100)
            if resp:
                screen.print(resp)
            else:
                break
        sock.close()
    is_on = not is_on
    hue_br.setGroup(1, on=is_on)
    screen.softbtn([("On" if is_on else "Off"), "Ready"])

def start(sta, conf):
    global sta_if
    global config
    global is_on
    global hue_br
    sta_if = sta
    config = conf
    while not sta_if.isconnected():
        sleep(1)
    screen.softbtn(["Off", "Ready"])
    for client in config["clients"]:
        addr_info = socket.getaddrinfo(client, 4444)
        addr = addr_info[0][-1]
        sock = socket.socket()
        sock.connect(addr)
        sock.send("1\r\n")
        while True:
            resp = sock.recv(100)
            if resp:
                screen.print(resp)
            else:
                break
        is_on = True
        screen.softbtn(["On", "Ready"])
        sock.close()
    screen.print("Find HUE")
    hue_br = hue.Bridge()
    hue_br.setGroup(1, on=True)
    btns = Buttons(screen, [(12, btn_cb)])

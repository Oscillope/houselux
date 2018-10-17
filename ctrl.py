from disp import Display
from buttons import Buttons
import network
import socket
import machine
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
    addrs = {}
    while True:
        if is_on:
            for client in config["clients"]:
                addr_info = socket.getaddrinfo(client, 4444)
                addrs[client] = addr_info[0][-1]
            for client in config["clients"]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    sock.sendto("hb\r\n", addrs[client])
                    sock.close()
                except OSError:
                    pass
        sleep_ms(700)

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
    prog = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
    if (prog.value() == 0):
        screen.print("Programming mode")
        sleep_ms(1000)
        import sys
        sys.exit()
    while not sta_if.isconnected():
        sleep_ms(250)
    _thread.start_new_thread(thread_func, ())
    screen.softbtn(["On", "Ready"])
    btns = Buttons(screen, [(12, btn_cb)])

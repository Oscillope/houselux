import machine
import network
import socket
from utime import sleep
import uio
import ujson

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
ap = network.WLAN(network.AP_IF)
ap.active(False)

is_on = False

try:
    conffile = uio.open("config", 'r')
    config = ujson.loads(conffile.read())
    conffile.close()
except OSError:
    import sys
    sys.exit()

def btn_cb():
    global is_on
    if not sta_if.isconnected():
        print("Tried to change state before connected")
        return
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
                print(resp)
            else:
                break
        sock.close()
    is_on = not is_on

sta_if.connect(config["ssid"], config["password"])
if (config["mode"] == "control"):
    from disp import Display
    from buttons import Buttons
    import hue
    screen = Display()
    screen.print("Hello!")
    screen.softbtn(["Off", "Conn..."])
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
elif (config["mode"] == "relay"):
    relay = machine.Pin(5, machine.Pin.OUT)
    relay.value(1) # Relay is active-low
    while not sta_if.isconnected():
        sleep(1)
    addr = socket.getaddrinfo('0.0.0.0', 4444)[0][-1]
    sock = socket.socket()
    sock.bind(addr)
    sock.listen(1)
    print("listening on", addr)

    while True:
        cl, cl_addr = sock.accept()
        print("connect from", cl_addr)
        cl_file = cl.makefile('rwb', 0)
        while True:
            line = cl_file.readline()
            print(line)
            if b'1' in line:
                is_on = True
                relay.value(0)
                break
            elif b'0' in line:
                is_on = False
                relay.value(1)
                break
            if not line or line == b'\r\n':
                break
        if is_on:
            cl.send("1 OK")
        else:
            cl.send("0 OK")
        cl.close()

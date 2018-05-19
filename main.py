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

sta_if.connect(config["ssid"], config["password"])
if (config["mode"] == "control"):
    import ctrl
    ctrl.start(sta_if, config)
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

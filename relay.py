import hue
import machine
import network
import socket
from utime import sleep_ms

def start(sta):
    global relay
    relay = machine.Pin(5, machine.Pin.OUT)
    relay.value(1) # Relay is active-low
    while not sta.isconnected():
        sleep_ms(500)
    addr = socket.getaddrinfo('0.0.0.0', 4444)[0][-1]
    sock = socket.socket()
    sock.bind(addr)
    sock.listen(1)
    print("listening on", addr)
    print("Find HUE")
    hue_br = hue.Bridge()

    while True:
        cl, cl_addr = sock.accept()
        cl.settimeout(2)
        print("connect from", cl_addr)
        while True:
            try:
                line = cl.readline()
            except OSError:
                print("timeout")
                break
            if not line or line == b'\r\n':
                break
            print(line)
            if b'hb' in line:
                relay.value(0)
                hue_br.setGroup(1, on=True)
        cl.close()
        relay.value(1)
        hue_br.setGroup(1, on=False)
        sleep_ms(100)

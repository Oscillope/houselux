import hue
import machine
import network
import socket
from utime import sleep_ms,ticks_ms,ticks_diff

def start(sta):
    global relay
    relay = machine.Pin(5, machine.Pin.OUT)
    relay.value(1) # Relay is active-low
    led = machine.Pin(2, machine.Pin.OUT)
    led.value(0) # LED is active-low
    while not sta.isconnected():
        sleep_ms(500)
    addr = socket.getaddrinfo('0.0.0.0', 4444)[0][-1]
    sock = socket.socket()
    sock.bind(addr)
    sock.listen(1)
    print("listening on", addr)
    print("Find HUE")
    hue_br = hue.Bridge()
    is_on = False
    led.value(1)

    while True:
        cl, cl_addr = sock.accept()
        cl.settimeout(2)
        last_time = ticks_ms()
        print("connect from", cl_addr)
        while True:
            try:
                line = cl.readline()
                time = ticks_ms()
            except OSError:
                print("timeout")
                break
            if not line or line == b'\r\n':
                break
            led.value(0)
            print(ticks_diff(time, last_time))
            last_time = time
            if b'hb' in line and not is_on:
                relay.value(0)
                hue_br.setGroup(1, on=True)
                is_on = True
            led.value(1)
        led.value(0)
        cl.close()
        relay.value(1)
        hue_br.setGroup(1, on=False)
        is_on = False
        led.value(1)
        sleep_ms(100)

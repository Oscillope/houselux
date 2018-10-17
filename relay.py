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
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(addr)
    sock.settimeout(1.5)
    print("listening on", addr)
    print("Find HUE")
    hue_br = hue.Bridge()
    is_on = False
    led.value(1)

    while True:
        last_time = ticks_ms()
        try:
            line = sock.recvfrom(1024)
            time = ticks_ms()
        except OSError:
            if is_on:
                led.value(0)
                relay.value(1)
                hue_br.setGroup(1, on=False)
                is_on = False
                led.value(1)
            sleep_ms(100)
            continue
        led.value(0)
        print(ticks_diff(time, last_time))
        last_time = time
        if b'hb' in line[0]:
            if not is_on:
                relay.value(0)
                hue_br.setGroup(1, on=True)
                is_on = True
        else:
            print(line)
        led.value(1)

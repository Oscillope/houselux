import hue
import machine
import network
import socket
from utime import sleep_ms,ticks_ms,ticks_diff

def start(sta):
    relay = machine.Pin(5, machine.Pin.OUT)
    relay.value(1) # Relay is active-low
    led = machine.Pin(2, machine.Pin.OUT)
    led.value(0) # LED is active-low
    while not sta.isconnected():
        sleep_ms(500)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((sta.ifconfig()[0], 4444))
    sock.settimeout(1.8)
    print("listening on " + sta.ifconfig()[0])
    print("Find HUE")
    hue_br = hue.Bridge()
    is_on = False
    led.value(1)

    while True:
        last_time = ticks_ms()
        try:
            line, addr = sock.recvfrom(1024)
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
        if b'hb' in line:
            if not is_on:
                relay.value(0)
                hue_br.setGroup(1, on=True)
                is_on = True
        elif b'off' in line:
            print(line)
            relay.value(1)
            hue_br.setGroup(1, on=False)
            is_on = False
            sock.sendto("off", addr)
        else:
            print(line)
        led.value(1)

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
    ctrl = ctrl.Control(sta_if)
    ctrl.start(config)
elif (config["mode"] == "relay"):
    import relay
    relay.start(sta_if)

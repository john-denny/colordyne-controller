from lib.vm_116_dmx import VM116
import time


with VM116() as dmx:

    end = time.time() + 5

    while time.time() < end:
        dmx.set_d65()
        time.sleep(0.05)
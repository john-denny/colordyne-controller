# Colordyne-controller
A small app to control ColorDyne, calibrated tuneable spectrum lights in the imaging lab in University of Galway

## Our setup
The lights are controlled via a DMX interface (a standard that uses the same connector as XLR, but is generally used for stage lighting), which is controllable via usb. The lighting configuration we (University of Galway's Imaging lab) has, uses 24 individually adressable leds. with channels as follows
245


## Using vm116 in your own project

The `vm116` package can be added to any Python project directly from this repository.

### Install
```
uv add git+https://github.com/john-denny/colordyne-controller
```
Or with pip:
```
pip install git+https://github.com/john-denny/colordyne-controller
```

### Usage

```python
from vm116 import VM116
import time


with VM116() as dmx:

    end = time.time() + 5
    
    while time.time() < end:
        dmx.set_d65()
        time.sleep(0.05)

    end = time.time() + 5
    dmx.brightness = 0.2
    while time.time() < end:
        dmx.set_d65()
        time.sleep(0.05)
from vm116 import VM116
```

You can also control individual channels:

```python
from vm116 import VM116

with VM116() as dmx:
    dmx.set_channel(1, 255)   # channel 1 → full
    dmx.set_channel(5, 128)   # channel 5 → half
    dmx.send()                # push to the bus
```

`brightness` is a multiplier (0.0–1.0) applied to all channel values at send time. It can be changed at any point without needing to re-set individual channels.

### Requirements

- Python 3.14+
- [pyusb](https://github.com/pyusb/pyusb) (installed automatically)
- On Windows: install a WinUSB driver for the VM116
- On Linux/macOS: run with `sudo`, or configure udev rules / a codeless kext

## Index
This is the current configuration for the colordyne lights in the imaging lab in university of galway

| DMX Channel | Name       | Wavelength (nm) | D65 Value (0-255) |
| ----------- | ---------- | --------------- | ----------------- |
| **1**       | lime       | 533             | 103               |
| **2**       | RYL B40    | 447             | 211               |
| **3**       | Violet421  | 422             | 131               |
| **4**       | lime       | 530             | 0                 |
| **5**       | DR-660     | 660             | 123               |
| **6**       | Violet405  | 404             | 191               |
| **7**       | pc-Amber   | 597             | 178               |
| **8**       | DR-735     | 735             | 255               |
| **9**       | red orange | 617             | 51                |
| **10**      | lime       | 535             | 183               |
| **11**      | DR-700     | 694             | 218               |
| **12**      | Sky Blue   | 473             | 240               |
| **13**      | NIR-940    | 942             | 0                 |
| **14**      | DR-680     | 677             | 109               |
| **15**      | lime       | 530             | 51                |
| **16**      | pc-Amber   | 596             | 0                 |
| **17**      | cyan 40    | 494             | 186               |
| **18**      | lime       | 533             | 212               |
| **19**      | FR-850     | 851             | 255               |
| **20**      | OS-640     | 636             | 78                |
| **21**      | lime       | 533             | 251               |
| **22**      | green      | 523             | 0                 |
| **23**      | amber      | 593             | 0                 |
| **24**      | lime       | 531             | 255               |
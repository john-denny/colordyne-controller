"""
dmx.py — Velleman VM116 / K8062 DMX controller driver

Hardware: Velleman VM116 (pre-assembled) / K8062 (kit)
Protocol: USB HID, low-speed, 8-byte interrupt transfers to endpoint 0x01
"""

import sys
import usb.core
import usb.util
import time

# USB identifiers
VENDOR_ID  = 0x10CF
PRODUCT_ID = 0x8062

# DMX universe size
DMX_CHANNELS = 512


class VM116:
    """
    Driver for the Velleman VM116 / K8062 USB DMX interface.

    Usage:
        dmx = VM116()
        dmx.set_channel(1, 255)   # channel 1 → full
        dmx.set_channel(2, 128)   # channel 2 → half
        dmx.send()                # push to the bus
        dmx.blackout()            # all channels → 0
        dmx.close()
    """

    def __init__(self, channel_count: int = 24, brightness: float=1):
        """
        Open the VM116.

        Args:
            channel_count: How many DMX channels to transmit (1–512).
            brightness: How bright is the light (1)
        """
        if not (1 <= channel_count <= DMX_CHANNELS):
            raise ValueError(f"channel_count must be 1–{DMX_CHANNELS}")

        self.channel_count = channel_count
        self._data = [0] * DMX_CHANNELS
        self.brightness = brightness
        # Find the device
        self._dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if self._dev is None:
            raise RuntimeError(
                "VM116 / K8062 not found. Is it plugged in?\n"
                "  Check with: python -c \"import usb.core; "
                "print(usb.core.find(idVendor=0x10CF, idProduct=0x8062))\""
            )

        # Detach the kernel HID driver on macOS/Linux so libusb can talk to
        # the device. Not needed (or available) on Windows — Zadig handles it.
        if sys.platform != "win32" and self._dev.is_kernel_driver_active(0):
            try:
                self._dev.detach_kernel_driver(0)
            except usb.core.USBError as e:
                raise RuntimeError(
                    f"Could not detach kernel driver: {e}\n"
                    "Try running with sudo, or install a codeless kext:\n"
                    "  https://github.com/njh/osc2k8062/tree/main/macosx"
                ) from e

        # Set configuration and claim interface
        self._dev.set_configuration()
        usb.util.claim_interface(self._dev, 0)

        # Warm up
        time.sleep(0.1)

        # Send empty data, to ensure the channel is open
        self.data = [0] * DMX_CHANNELS
        self._send_dmx()



    @property
    def brightness(self) -> float:
        return self._brightness

    @brightness.setter
    def brightness(self, value: float) -> None:
        if not (0.0 <= value <= 1.0):
            raise ValueError("brightness must be between 0.0 and 1.0")
        self._brightness = float(value)

    def set_channel(self, channel: int, value: int) -> None:
        """
        Set a single DMX channel value (does not transmit yet).

        Args:
            channel: 1-indexed DMX channel number (1–512)
            value:   Brightness/level (0–255)
        """
        if not (1 <= channel <= DMX_CHANNELS):
            raise ValueError(f"channel must be 1–{DMX_CHANNELS}")
        if not (0 <= value <= 255):
            raise ValueError("value must be 0–255")
        self._data[channel - 1] = int(value * self.brightness)

    def set_channels(self, values: dict) -> None:
        """
        Set multiple channels at once.

        Args:
            values: {channel_number: value, ...}  e.g. {1: 255, 2: 128, 3: 0}
        """
        for ch, val in values.items():
            self.set_channel(ch, val)

    def set_d65(self) -> None:
        """
        Set's the channels to the calibrated d65 values
        """
        self.set_channels({
            1: 103, 2: 211, 3: 131, 4:   0, 5: 123,
            6: 191, 7: 178, 8: 255, 9:  51, 10: 183,
            11: 218, 12: 240, 13:  0, 14: 109, 15:  51,
            16:  0, 17: 186, 18: 212, 19: 255, 20:  78,
            21: 251, 22:  0, 23:  0, 24: 255,
        })
        self.send()


    def set_all(self, value: int) -> None:
        """Set all channels to the same value (does not transmit yet)."""
        if not (0 <= value <= 255):
            raise ValueError("value must be 0–255")
        for i in range(self.channel_count):
            self._data[i] = value

    def send(self) -> None:
        """Transmit the current channel state to the device."""
        self._send_dmx()

    def blackout(self) -> None:
        """Set all channels to 0 and transmit."""
        self.set_all(0)
        self.send()

    def close(self) -> None:
        """Release the USB interface."""
        try:
            usb.util.release_interface(self._dev, 0)
        except Exception:
            pass

    # Context manager support
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ------------------------------------------------------------------ #
    #  Protocol implementation                                            #
    # ------------------------------------------------------------------ #

    def _write_packet(self, data: list) -> None:
        """Send one 8-byte HID interrupt packet to endpoint 0x01."""
        assert len(data) == 8, "Packets must be exactly 8 bytes"
        self._dev.write(0x01, bytes(data), timeout=20)

    def _send_dmx(self) -> None:
        """
        Build and send the sequence of 8-byte packets that represent
        the current DMX frame, using Velleman's zero-compression scheme.

        Protocol reverse-engineered from k8062forlinux / osc2k8062.c
        (Denis Moreaux / Nicholas Humfrey, GPL v2).

        Packet types:
          cmd 4 — frame start: skip N leading zeros, then 6 channels
          cmd 5 — mid-stream zero skip, then 6 channels
          cmd 2 — 7 consecutive non-zero channels
          cmd 3 — 1 remaining channel (used for tail)
        """
        ch = self._data
        n  = self.channel_count

        # --- Packet 1: cmd 4 — count leading zeros, send first 6 values ---
        # Count how many leading channels are zero (up to 100)
        i = 0
        while i < min(100, n - 6) and not ch[i]:
            i += 1

        pkt = [4, i + 1,
               ch[i],     ch[i + 1], ch[i + 2],
               ch[i + 3], ch[i + 4], ch[i + 5]]
        self._write_packet(pkt)
        i += 6

        # --- Middle packets ---
        while i < n - 7:
            if not ch[i]:
                # Current channel is zero — find the next non-zero run
                n_skip = 0
                j = i + 1
                while j < n - 6 and j - i < 100 and not ch[j]:
                    j += 1
                n_skip = j - i  # number of zeros we skipped

                pkt = [5, n_skip,
                       ch[j],     ch[j + 1], ch[j + 2],
                       ch[j + 3], ch[j + 4], ch[j + 5]]
                self._write_packet(pkt)
                i = j + 6
            else:
                # cmd 2 — 7 consecutive channels
                pkt = [2,
                       ch[i],     ch[i + 1], ch[i + 2], ch[i + 3],
                       ch[i + 4], ch[i + 5], ch[i + 6]]
                self._write_packet(pkt)
                i += 7

        # --- Tail: send remaining channels one at a time (cmd 3) ---
        while i < n:
            pkt = [3, ch[i], 0, 0, 0, 0, 0, 0]
            self._write_packet(pkt)
            i += 1


# ------------------------------------------------------------------ #
#  Example / demo                                                     #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    print("VM116 DMX demo — 24 channels")
    print("Ctrl-C to stop\n")

    with VM116(channel_count=24) as dmx:

        print("Fade all 24 channels up...")
        for level in range(0, 256, 5):
            dmx.set_all(level)
            dmx.send()
            time.sleep(0.05)

        print("Hold at full for 1 second...")
        time.sleep(1)

        print("Fade back down...")
        for level in range(255, -1, -5):
            dmx.set_all(level)
            dmx.send()
            time.sleep(0.05)

        print("Set channels individually: 1→255, 2→128, 3→64")
        dmx.blackout()
        dmx.set_channels({1: 255, 2: 128, 3: 64})
        dmx.send()
        time.sleep(2)

        print("Blackout.")
        dmx.blackout()

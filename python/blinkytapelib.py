#!/usr/bin/python3

import collections as _collections
import serial as _serial
import struct as _struct
import sys as _sys
import threading as _threading
import time as _time

class Display:
    def __init__(self):
        self._lights = [_dark_light for x in range(60)]
        self._updates = _collections.deque()

    def clear(self):
        for i in range(60):
            self.update(i, _dark_light)

    def update(self, index, light):
        self._updates.appendleft((index, light))

    def _process_updates(self):
        while True:
            try:
                update = self._updates.pop()
            except IndexError:
                break

            self._lights[update[0]] = update[1]

class Light:
    def __init__(self, red=0, green=0, blue=0, blinky=False):
        self._bytes = _struct.pack("BBB", red, green, blue)
        self._blinky = blinky

    def __repr__(self):
        return f"{self.__class__.__name__}({self._bytes},{self._blinky})"

_dark_light = Light()

class DisplayThread(_threading.Thread):
    def __init__(self, display, device_port):
        super().__init__()

        self._display = display
        self._device = _Device(device_port)

        self._stopping = _threading.Event()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self._stopping.set()

    def run(self):
        with self._device.open():
            while not self._stopping.is_set():
                self._display._process_updates()

                for light in self._display._lights:
                    self._device.write(light._bytes)

                self._device.show()
                _time.sleep(2.9)

                for light in self._display._lights:
                    if light._blinky:
                        self._device.write(_dark_light._bytes)
                    else:
                        self._device.write(light._bytes)

                self._device.show()
                _time.sleep(0.1)

class _Device:
    def __init__(self, port):
        self._port = port
        self._serial = None

    def open(self):
        assert self._serial is None

        self._serial = _serial.Serial(self._port, 115200)

        return self._serial

    def write(self, pixel_bytes):
        assert len(pixel_bytes) % 3 == 0

        pixel_bytes = pixel_bytes.replace(b"\xFF", b"\xFE")

        self._serial.write(pixel_bytes)

    def flush(self):
        self._serial.flush()
        self._serial.flushInput()

    def show(self):
        self._serial.write(b"\xFF")
        self.flush()

def _main():
    display = Display()

    with DisplayThread(display, _sys.argv[1]):
        for i in range(12):
            if i % 3 == 0:
                display.update(0, Light(255, 0, 0))
            elif i % 3 == 1:
                display.update(0, Light(0, 255, 0))
            else:
                display.update(0, Light(0, 0, 255))

            _time.sleep(1)

if __name__ == "__main__":
    try:
        _main()
    except KeyboardInterrupt:
        pass

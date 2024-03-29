#!/usr/bin/python3

import collections as _collections
import serial as _serial
import struct as _struct
import sys as _sys
import threading as _threading
import time as _time
import traceback as _traceback

class Tape:
    def __init__(self):
        self._lights = [_dark_light for x in range(60)]
        self._updates = _collections.deque()

    def clear(self):
        self.update(None, _dark_light)

    def update(self, index, light):
        self._updates.appendleft((index, light))

    def _process_updates(self):
        while True:
            try:
                index, light = self._updates.pop()
            except IndexError:
                break

            if index is None:
                self._lights = [light for x in range(60)]
            else:
                self._lights[index] = light

class Light:
    def __init__(self, red=0, green=0, blue=0):
        self._bytes = _struct.pack("BBB", red, green, blue)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._bytes})"

_dark_light = Light()

class TapeThread(_threading.Thread):
    def __init__(self, tape, device_port):
        super().__init__()

        self._tape = tape
        self._device = _Device(device_port)

        self._stopping = _threading.Event()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()

    def stop(self):
        self._stopping.set()

    def run(self):
        while True:
            if self._stopping.is_set():
                break

            try:
                self.do_run()
            except KeyboardInterrupt:
                raise
            except OSError:
                pass
            except:
                _traceback.print_exc()

            _time.sleep(2)

    def do_run(self):
        with self._device.open():
            while True:
                self._tape._process_updates()

                for light in self._tape._lights:
                    self._device.write(light._bytes)

                self._device.show()

                _time.sleep(2)

                if self._stopping.is_set():
                    self._device.clear()
                    break

class _Device:
    def __init__(self, port):
        self._port = port
        self._serial = None

    def open(self):
        self._serial = _serial.Serial(self._port, 115200, exclusive=True)
        return self._serial

    def write(self, pixel_bytes):
        assert len(pixel_bytes) % 3 == 0

        pixel_bytes = pixel_bytes.replace(b"\xFF", b"\xFE")

        self._serial.write(pixel_bytes)

    def flush(self):
        self._serial.flush()
        self._serial.reset_input_buffer()

    def show(self):
        self._serial.write(b"\xFF")
        self.flush()

    def clear(self):
        self.write(b"\x00\x00\x00" * 60)
        self.show()

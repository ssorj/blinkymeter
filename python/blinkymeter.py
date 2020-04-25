#!/usr/bin/python3

import collections as _collections
import requests as _requests
import sys as _sys
import time as _time

from blinkytapelib import *

_yellow_light = Light(255, 255, 0)
_green_light = Light(0, 255, 0)
_solid_red_light = Light(255, 0, 0)
_blinky_red_light = Light(255, 0, 0, blinky=True)

def fetch_data(data_url):
    try:
        response = _requests.get(data_url)
        response.raise_for_status()
    except Exception as e:
        return None, e

    return response.json(), None

def show_fetch_error(display):
    display.clear()
    display.update(59, _yellow_light)

def show_results(display, data):
    green_lights = list()
    solid_red_lights = list()
    blinky_red_lights = list()

    for job_id, job_data in data["jobs"].items():
        result = job_data["current_result"]

        if result is None:
            continue

        if result["status"] == "PASSED":
            green_lights.append(_green_light)

        if result["status"] == "FAILED":
            prev = job_data["previous_result"]

            if prev is not None and prev["status"] == "PASSED":
                blinky_red_lights.append(_blinky_red_light)
            else:
                solid_red_lights.append(_solid_red_light)

    lights = blinky_red_lights + solid_red_lights + green_lights

    display.clear()

    for i, j in enumerate(range(59, -1, -2)):
        display.update(j, lights[i])

def main():
    device_port, data_url = _sys.argv[1:]
    display = Display()

    with DisplayThread(display, device_port):
        while True:
            data, error = fetch_data(data_url)

            if error:
                show_fetch_error(display)
            else:
                show_results(display, data)

            for i in range(30):
                _time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

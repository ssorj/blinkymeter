#!/usr/bin/python3

import collections as _collections
import requests as _requests
import sys as _sys
import time as _time

from blinkytapelib import *

def fetch_data():
    data = None
    error = None

    try:
        data = _requests.get("https://blinky-rhm.cloud.paas.psi.redhat.com/data.json").json()
    except Exception as e:
        print(e)
        error = e

    return data, error

def show_error(display):
    display.clear()
    display.update(59, Light(255, 255, 0))

def show_results(display, data):
    pass_light = Light(0, 255, 0)
    fail_light = Light(255, 0, 0)
    blinky_fail_light = Light(255, 0, 0, blinky=True)

    pass_lights = list()
    fail_lights = list()
    blinky_fail_lights = list()

    for job_id, job_data in data["jobs"].items():
        result = job_data["current_result"]

        if result is None:
            continue

        group_id = job_data["group_id"]
        group_data = data["groups"][str(group_id)]
        category_id = group_data["category_id"]
        category_data = data["categories"][str(category_id)]

        if category_data["key"] == "broker":
            continue

        if result["status"] == "PASSED":
            pass_lights.append(pass_light)

        if result["status"] == "FAILED":
            prev = job_data["previous_result"]

            if prev is not None and prev["status"] == "PASSED":
                blinky_fail_lights.append(blinky_fail_light)
            else:
                fail_lights.append(fail_light)

    lights = blinky_fail_lights + fail_lights + pass_lights

    display.clear()

    for i, j in enumerate(range(59, -1, -2)):
        display.update(j, lights[i])

def main():
    display = Display()

    with DisplayThread(display, _sys.argv[1]):
        while True:
            data, error = fetch_data()

            if error:
                show_error(display)
            else:
                show_results(display, data)

            for i in range(60):
                _time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

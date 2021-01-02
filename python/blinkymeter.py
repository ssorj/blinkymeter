#!/usr/bin/python3

import collections as _collections
import requests as _requests
import sys as _sys
import time as _time

from blinkytapelib import *

_yellow_light = Light(255, 255, 0)
_green_light = Light(0, 255, 0)
_red_light = Light(255, 0, 0)

def fetch_data(data_url):
    try:
        response = _requests.get(data_url)
        response.raise_for_status()
    except Exception as e:
        return None, e

    return response.json(), None

def show_fetch_error(tape):
    tape.clear()
    tape.update(59, _yellow_light)

def show_results(tape, data, categories):
    green_lights = list()
    red_lights = list()

    for job_id, job_data in data["jobs"].items():
        group_data = data["groups"][str(job_data["group_id"])]
        category_data = data["categories"][str(group_data["category_id"])]

        if category_data["key"] not in categories:
            continue

        result = job_data["current_result"]

        if result is None:
            continue

        if result["status"] == "PASSED":
            green_lights.append(_green_light)

        if result["status"] == "FAILED":
            red_lights.append(_red_light)

    lights = red_lights + green_lights

    tape.clear()

    for i, j in enumerate(range(59, -1, -2)):
        if i == len(lights):
            break

        tape.update(j, lights[i])

def main():
    data_url = _sys.argv[1]
    device_mappings = _sys.argv[2:]

    tapes = list()
    threads = list()

    for device, categories in zip(device_mappings[0::2], device_mappings[1::2]):
        categories = categories.split(",")
        tape = Tape()
        thread = TapeThread(tape, device)

        tapes.append((tape, categories))
        threads.append(thread)

    for thread in threads:
        thread.start()

    try:
        while True:
            data, error = fetch_data(data_url)

            if error:
                for tape, _ in tapes:
                    show_fetch_error(tape)
            else:
                for tape, categories in tapes:
                    show_results(tape, data, categories)

            for i in range(30):
                _time.sleep(2)
    finally:
        for thread in threads:
            thread.stop()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

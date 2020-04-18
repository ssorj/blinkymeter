export PYTHONPATH := python

.PHONY: run
run:
	python3 python/blinkymeter.py /dev/ttyACM0 "https://blinky-rhm.cloud.paas.psi.redhat.com/data.json"

.PHONY: clean
clean:
	rm -rf python/__pycache__

export PYTHONPATH := python

.PHONY: run
run:
	python3 python/blinkymeter.py ${BLINKY_DATA_URL} /dev/ttyACM0 /dev/ttyACM1 /dev/ttyACM2

.PHONY: clean
clean:
	rm -rf python/__pycache__

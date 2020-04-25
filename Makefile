export PYTHONPATH := python

.PHONY: run
run:
	python3 python/blinkymeter.py /dev/ttyACM0 ${BLINKY_DATA_URL}

.PHONY: clean
clean:
	rm -rf python/__pycache__

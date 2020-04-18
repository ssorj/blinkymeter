export PYTHONPATH := python

.PHONY: run
run:
	python3 python/blinkymeter.py /dev/ttyACM0

.PHONY: clean
clean:
	rm -rf python/__pycache__

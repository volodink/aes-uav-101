all: clean
	echo "Global main"
	cd drones-101 && make
	cd firedetection-101/lecture && make
	cd platformio-101/lecture && make

clean:
	echo "Cleaup."

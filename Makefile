all: clean
	echo "Global main"
	cd drones-101 && make
	cd firedetection-101/lecture && make
	cd firedetection-101 && mkdir dist && zip -r dist/firedetector-final.zip firedetector-final/*.py firedetector-final/*.txt
	
clean:
	echo "Cleaup."
	rm -rf firedetection-101/dist
	rm -rf firedetection-101/lecture/dist
	rm -rf drones-101/dist
	rm -rf platformio-101/dist

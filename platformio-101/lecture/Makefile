all: clean
	marp src/platformio-101.md -o dist/platformio-101/platformio-101.pdf
	marp src/platformio-101.md -o dist/platformio-101/live/platformio-101.html
	cp -r src/img dist/platformio-101/live

live:
	marp -p --server ./src

clean:
	rm -rf dist
	rm -rf build
	rm -rf builds

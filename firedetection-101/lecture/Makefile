all: clean
	marp src/firedetection-101.md -o dist/firedetection-101/firedetection-101.pdf
	marp src/firedetection-101.md -o dist/firedetection-101/live/firedetection-101.html
	cp -r src/img dist/firedetection-101/live

live:
	marp -p --server ./src

clean:
	rm -rf dist
	rm -rf build
	rm -rf builds

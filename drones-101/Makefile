all: clean
	java -jar ../.devcontainer/lib/plantuml.jar src/diagrams/*.puml
	marp src/drones-101.md -o dist/drones-101/drones-101.pdf
	marp src/drones-101.md -o dist/drones-101/live/drones-101.html
	cp -r src/img dist/drones-101/live
	cp -r src/diagrams dist/drones-101/live

live:
	marp -p --server ./src

clean:
	rm -rf dist
	rm -rf build
	rm -rf builds
	rm -rf src/diagrams/*.png

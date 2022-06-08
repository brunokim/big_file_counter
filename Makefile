
build:
	docker build . -t big_file_counter

run:
	docker run \
		--memory 100m --memory-swap 100m \
		-e FILENAME=big_file_1m.txt \
		-e MAX_MEMORY_OCCUPANCY=0.70 \
		-e REPORT_INTERVAL=0.1 \
		big_file_counter | gzip -c > output.log.gz


build:
	docker build . -t big_file_counter

run:
	docker run \
		--memory 50m --memory-swap 50m \
		-e FILENAME=big_file_1m.txt \
		-e MEMORY_LIMIT=25M \
		big_file_counter > /dev/null

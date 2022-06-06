
build:
	docker build . -t big_file_counter

run:
	docker run \
		--memory 100m --memory-swap 100m \
		-e FILENAME=big_file_1m.txt \
		-e MEMORY_LIMIT=90M \
		big_file_counter > /dev/null

FROM python:3

WORKDIR /app

COPY human_size.py make_file.py ./
RUN python make_file.py --num_elements=3 --filename=big_file_3.txt
RUN python make_file.py --num_elements=1_000 --filename=big_file_1k.txt
RUN python make_file.py --num_elements=1_000_000 --filename=big_file_1m.txt

COPY count_file_lines.py ./
CMD python count_file_lines.py --filename "${FILENAME}" --memory_limit "${MEMORY_LIMIT}"

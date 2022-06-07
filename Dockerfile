FROM python:3

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY human_size.py make_file.py ./
RUN python make_file.py --num_elements=3 --filename=big_file_3.txt
RUN python make_file.py --num_elements=1_000 --filename=big_file_1k.txt
RUN python make_file.py --num_elements=1_000_000 --filename=big_file_1m.txt

COPY runtime.py count_file_lines.py ./
CMD python count_file_lines.py --filename "${FILENAME}" --max_memory_occupancy "${MAX_MEMORY_OCCUPANCY:-0.75}" --report_interval "${REPORT_INTERVAL:-1}"

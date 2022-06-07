from collections import Counter
from copy import copy
from human_size import parse_size, format_size
import io
from runtime import print_report
import sys
from time import time


class LineCounter:
    def __init__(self, memory_limit: int = 1 << 20, check_interval: int = 1024, report_interval_sec: float = 1.0):
        self.cnt: Counter[str] = Counter()
        self.last_time: float = 0.0

        self.memory_limit = memory_limit
        self.check_interval = check_interval
        self.report_interval_sec = report_interval_sec

        self.content_size: int = 0

    def read(self, f: io.TextIOBase) -> Counter[str]:
        self.cnt.clear()
        self.content_size = 0
        self.last_time = 0.0
        for i, line in enumerate(f):
            word = line[:-1]
            self.cnt[word] += 1
            # If first insertion, account for word size.
            if self.cnt[word] == 1:
                self.content_size += sys.getsizeof(word)
            # Check counter size periodically.
            if i % self.check_interval == 0:
                self.check_counter_size()
                self.report_memory_status(i)
        return copy(self.cnt)

    def check_counter_size(self) -> None:
        cnt_size = sys.getsizeof(self.cnt)
        # This calculation makes it closer to the actual limit when the container is killed for OOM.
        if cnt_size + 2*self.content_size > self.memory_limit:
            raise MemoryError('Memory limit exceeded')

    def report_memory_status(self, i: int) -> None:
        now = time()
        if now < self.last_time + self.report_interval_sec:
            return
        self.last_time = now

        cnt_size = sys.getsizeof(self.cnt)
        print_report({'counter size': cnt_size, 'content size': self.content_size}, print_header=(i == 0))


def main(filename: str, memory_limit: int, report_interval: float) -> None:
    line_counter = LineCounter(memory_limit=memory_limit, report_interval_sec=report_interval)
    with open(filename) as f:
        cnt = line_counter.read(f)
    for elem, freq in cnt.most_common():
        print(f'{elem} - {freq}')


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--filename', type=str, default='big_file.txt', help='Filename to count line frequency')
    parser.add_argument('--memory_limit', type=parse_size, default='10m', help='Memory limit to enforce in application')
    parser.add_argument('--report_interval', type=float, default=1, help='Reporting interval, in seconds')
    args = parser.parse_args()

    main(args.filename, args.memory_limit, args.report_interval)

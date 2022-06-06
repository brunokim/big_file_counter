from collections import Counter
from copy import copy
from human_size import parse_size, format_size
import io
import sys
from time import time


class LineCounter:
    def __init__(self, memory_limit: int = 1 << 20, check_interval: int = 1024):
        self.cnt: Counter[str] = Counter()
        self.last_time: float = 0.0

        self.memory_limit = memory_limit
        self.check_interval = check_interval

    def read(self, f: io.TextIOBase) -> Counter[str]:
        self.cnt.clear()
        self.last_time = 0.0
        for i, line in enumerate(f):
            self.cnt[line[:-1]] += 1
            if i % self.check_interval != 0:
                continue
            self.check_counter_size()
        return copy(self.cnt)

    def check_counter_size(self) -> None:
        cnt_size = sys.getsizeof(self.cnt)
        content_size = sum(sys.getsizeof(key) for key in self.cnt)
        now = time()
        if now > self.last_time + 1:
            print(f'counter size: {format_size(cnt_size)}, content size: {format_size(content_size)}', file=sys.stderr)
            self.last_time = now
        if cnt_size + content_size > self.memory_limit:
            raise MemoryError('Memory limit exceeded')


def main(filename: str, memory_limit: int) -> None:
    line_counter = LineCounter(memory_limit=memory_limit)
    with open(filename) as f:
        cnt = line_counter.read(f)
    for elem, freq in cnt.most_common():
        print(f'{elem} - {freq}')


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--filename', type=str, default='big_file.txt', help='Filename to count line frequency')
    parser.add_argument('--memory_limit', type=parse_size, default='10m', help='Memory limit to enforce in application')
    args = parser.parse_args()

    main(args.filename, args.memory_limit)

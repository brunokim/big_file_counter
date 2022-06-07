from copy import copy
import gc
from human_size import parse_size, format_size
import io
import os
from runtime import memory_working_set, memory_limit, print_report
from sortedcontainers import SortedDict
import sys
import tempfile
from time import time


class LineCounter:
    def __init__(self, max_memory_occupancy: float = 0.90, report_interval_sec: float = 1.0):
        self.cnt: SortedDict[str, int] = SortedDict()
        self.last_time: float = 0.0

        self.max_memory_occupancy = max_memory_occupancy
        self.report_interval_sec = report_interval_sec

        self.drop_sizes: list[int] = []
        self.tempfiles: list[tempfile.TemporaryFile] = []
        self.check_interval: int = 1024
        self.max_memory: int = int(memory_limit() * max_memory_occupancy)

    def read(self, f: io.TextIOBase) -> dict[str, int]:
        self.cnt.clear()
        self.last_time = 0.0
        self.drop_sizes = []
        for i, line in enumerate(f):
            word = line[:-1]
            if word not in self.cnt:
                self.cnt[word] = 0
            self.cnt[word] += 1
            # Check counter size periodically.
            if i % self.check_interval == 0:
                self.check_memory_usage()
                self.report_memory_status(i)
        print(f'Drops: {len(self.drop_sizes)}', file=sys.stderr)
        for i, (tempname, size) in enumerate(zip(self.tempfiles, self.drop_sizes)):
            print(f'  #{i:>03d}: {size:> 4d} items in {tempname}', file=sys.stderr)
        return copy(self.cnt)

    def check_memory_usage(self) -> None:
        mem = memory_working_set()
        if mem > self.max_memory:
            # Dump counter to tempfile
            fd, tempname = tempfile.mkstemp(text=True)
            try:
                f = os.fdopen(fd, mode='w+')
                for key, freq in self.cnt.items():
                    f.write(f'{key}\t{freq}\n')
                self.tempfiles.append(tempname)
            finally:
                os.close(fd)

            self.drop_sizes.append(len(self.cnt))
            self.cnt.clear()
            gc.collect()

    def report_memory_status(self, i: int) -> None:
        now = time()
        if now < self.last_time + self.report_interval_sec:
            return
        self.last_time = now

        print_report(print_header=(i == 0))


def main(filename: str, max_memory_occupancy: int, report_interval: float) -> None:
    line_counter = LineCounter(max_memory_occupancy=max_memory_occupancy, report_interval_sec=report_interval)
    with open(filename) as f:
        cnt = line_counter.read(f)
    for elem, freq in sorted(cnt.items(), key=lambda item: item[1], reverse=True):
        print(f'{elem} - {freq}')


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--filename', type=str, default='big_file.txt', help='Filename to count line frequency')
    parser.add_argument('--max_memory_occupancy', type=float, default=0.7, help='Fraction of memory to allow usage')
    parser.add_argument('--report_interval', type=float, default=1, help='Reporting interval, in seconds')
    args = parser.parse_args()

    main(args.filename, args.max_memory_occupancy, args.report_interval)

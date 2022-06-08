from copy import copy
from dataclasses import dataclass
import gc
from human_size import parse_size, format_size
import io
import os
import re
from runtime import memory_working_set, memory_limit, print_report
from sortedcontainers import SortedDict
import sys
import tempfile
from time import time


def write_count(f, key: str, count: int):
    f.write(f'{key}\t{count}\n')


def read_count(f):
    line = f.readline()
    if not line:
        return None, None
    m = re.match(r'(.*)\t(\d+)\n', line)
    if not m:
        raise ValueError(f'Invalid entry in file line: {line!r}')
    key, count_str = m.groups()
    return key, int(count_str)


class ExternalCounter:
    def __init__(self, filename):
        self.filename = filename

    def items(self):
        with open(self.filename) as f:
            key, count = read_count(f)
            while key is not None:
                yield key, count
                key, count = read_count(f)


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

    def reset(self) -> None:
        self.cnt.clear()
        self.last_time = 0.0
        self.drop_sizes = []

    def read(self, f: io.TextIOBase) -> dict[str, int]:
        self.reset()
        for i, line in enumerate(f):
            word = line[:-1]
            if word not in self.cnt:
                self.cnt[word] = 0
            self.cnt[word] += 1
            # Check counter size periodically.
            if i % self.check_interval == 0:
                self.check_memory_usage()
                self.report_memory_status(i)
        if self.tempfiles:
            print('Temp files:', file=sys.stderr)
            for filename, size in zip(self.tempfiles, self.drop_sizes):
                print(f'  {filename}: {size} records', file=sys.stderr)
            merged_temp, num_records = merge_files(self.tempfiles)
            print(f'Merged {num_records} in {merged_temp} across {len(self.tempfiles)} files', file=sys.stderr)
            return ExternalCounter(merged_temp)
        return copy(self.cnt)

    def check_memory_usage(self) -> None:
        mem = memory_working_set()
        if mem > self.max_memory:
            # Dump counter to tempfile
            fd, tempname = tempfile.mkstemp(text=True)
            try:
                f = os.fdopen(fd, mode='w+')
                for key, freq in self.cnt.items():
                    write_count(f, key, freq)
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


@dataclass
class FileState:
    name: str
    fp: io.TextIOBase = None
    line: int = 0
    key: str = None
    count: int = None

    def open(self):
        self.fp = open(self.name)

    def read(self):
        if self.is_closed:
            return
        if self.key is not None:
            return
        key, count = read_count(self.fp)
        if key is None:
            self.fp.close()
            self.fp = None
            return
        self.line += 1
        self.key = key
        self.count = count

    @property
    def is_closed(self):
        return self.fp is None


def merge_files(filenames):
    fd, tempname = tempfile.mkstemp(text=True)
    try:
        target = os.fdopen(fd, mode='w')

        files = [FileState(filename) for filename in filenames]
        [f.open() for f in files]
        num_records = 0
        while files:
            [f.read() for f in files]
            files = [f for f in files if not f.is_closed]
            if not files:
                break
            min_key = min(f.key for f in files)
            total = 0
            for f in files:
                if f.key == min_key:
                    f.key = None
                    total += f.count
            write_count(target, min_key, total)
            num_records += 1
    finally:
        os.close(fd)
    return tempname, num_records


def main(filename: str, max_memory_occupancy: int, report_interval: float) -> None:
    line_counter = LineCounter(max_memory_occupancy=max_memory_occupancy, report_interval_sec=report_interval)
    with open(filename) as f:
        cnt = line_counter.read(f)
    for elem, freq in cnt.items():
        print(f'{elem} - {freq}')


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--filename', type=str, default='big_file.txt', help='Filename to count line frequency')
    parser.add_argument('--max_memory_occupancy', type=float, default=0.7, help='Fraction of memory to allow usage')
    parser.add_argument('--report_interval', type=float, default=1, help='Reporting interval, in seconds')
    args = parser.parse_args()

    main(args.filename, args.max_memory_occupancy, args.report_interval)

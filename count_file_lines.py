from collections import Counter
from human_size import parse_size, format_size
import io
import sys
from time import time


def count_lines(f: io.TextIOBase, memory_limit: int = 1 << 20, check_interval: int = 1024) -> Counter[str]:
    cnt: Counter[str] = Counter()
    time_of_last_report: float = 0.0
    for i, line in enumerate(f):
        cnt[line[:-1]] += 1
        if i % check_interval != 0:
            continue
        cnt_size = sys.getsizeof(cnt)
        content_size = sum(sys.getsizeof(key) for key in cnt)
        now = time()
        if now > time_of_last_report + 1:
            print(f'counter size: {format_size(cnt_size)}, content size: {format_size(content_size)}', file=sys.stderr)
            time_of_last_report = now
        if cnt_size + content_size > memory_limit:
            raise MemoryError('Memory limit exceeded')
    return cnt


def main(filename: str, memory_limit: int) -> None:
    with open(filename) as f:
        cnt = count_lines(f, memory_limit)
    for elem, freq in cnt.most_common():
        print(f'{elem} - {freq}')


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--filename', type=str, default='big_file.txt', help='Filename to count line frequency')
    parser.add_argument('--memory_limit', type=parse_size, default='10m', help='Memory limit to enforce in application')
    args = parser.parse_args()

    main(args.filename, args.memory_limit)

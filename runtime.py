from human_size import format_size
import sys


def memory_usage() -> int:
    with open('/sys/fs/cgroup/memory/memory.memsw.usage_in_bytes') as f:
        return int(f.read())


def memory_working_set() -> int:
    usage = memory_usage()
    inactive = memory_stats()['inactive_file']
    return usage - inactive


def memory_max_usage() -> int:
    with open('/sys/fs/cgroup/memory/memory.memsw.max_usage_in_bytes') as f:
        return int(f.read())


def kernel_memory_usage() -> int:
    with open('/sys/fs/cgroup/memory/memory.kmem.usage_in_bytes') as f:
        return int(f.read())


def memory_limit() -> int:
    with open('/sys/fs/cgroup/memory/memory.memsw.limit_in_bytes') as f:
        return int(f.read())


def memory_stats() -> dict[str, int]:
    stats: dict[str, int] = {}
    with open('/sys/fs/cgroup/memory/memory.stat') as f:
        for line in f:
            name, value_str = line.strip().split(' ')
            stats[name] = int(value_str)
    return stats


def print_report(report: dict[str, int] = None, print_header: bool = False) -> None:
    if report is None:
        report = {}
    report = report.copy()

    stats = memory_stats()
    report.update({
        'approx usage': memory_usage(),
        'kernel usage': kernel_memory_usage(),
        'total cache': stats['total_cache'],
        'total rss': stats['total_rss'],
        'total swap': stats['total_swap'],
        'inactive file': stats['inactive_file'],
        'limit': memory_limit(),
    })
    width = max(len(key) for key in report) + 2

    if print_header:
        for metric in report:
            print(f'{metric:>{width}} ', file=sys.stderr, end='')
        print(file=sys.stderr)
    for value in report.values():
        print(f'{format_size(value):>{width}} ', file=sys.stderr, end='')
    print(file=sys.stderr)





def memory_usage() -> int:
    with open('/sys/fs/cgroup/memory/memory.usage_in_bytes') as f:
        return int(f.read())


def memory_limit() -> int:
    with open('/sys/fs/cgroup/memory/memory.limit_in_bytes') as f:
        return int(f.read())


def memory_stats() -> dict[str, int]:
    stats: dict[str, int] = {}
    with open('/sys/fs/cgroup/memory/memory.stat') as f:
        for line in f:
            name, value_str = line.strip().split(' ')
            stats[name] = int(value_str)
    return stats

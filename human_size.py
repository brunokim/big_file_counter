import re

UNITS = {
    'k': 1 << 10,
    'm': 1 << 20,
    'g': 1 << 30,
}


def parse_size(text: str) -> int:
    """Parse human-readable number of bytes.

    >>> parse_size("1k")
    1024
    >>> parse_size("3.02 MiB")
    3166699
    """
    m = re.match(r'''(?xi) # verbose, case-insensitive
        ^                  # start of string
        (\d+               # one or more digits
         (?:\.\d+)?        # optional '.' followed by digits, not captured
        )
        \s*                # any number of space characters
        (?:
         ([kmg])           # kilo, mega, giga prefix
         (?:iB|B)?         # optional complement to prefix (KiB, KB), not captured
        )?                 # suffix is optional
        $                  # end of string
    ''', text)
    if not m:
        raise ValueError(f'Invalid format for number of bytes')
    size_str, suffix = m.groups()
    unit = UNITS.get(suffix.lower(), 1)
    size = float(size_str)
    return int(size * unit)


SUFFIX = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']


def format_size(size: int) -> str:
    suffix_pos = 0 
    while size > 1024:
        size /= 1024
        suffix_pos += 1
    suffix = SUFFIX[suffix_pos]
    return f'{size:.2f} {suffix}'

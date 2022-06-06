from human_size import parse_size
import random


def create_file(num_elements: int, size: int, filename: str) -> int:
    with open(filename, 'w') as f:
        total = 0
        while total < size:
            value = random.randrange(num_elements)
            total += f.write(f'{value}\n')
    return total


def main(num_elements: int, size: int, filename: str) -> None:
    total = create_file(num_elements, size, filename)
    print(f'{total} bytes written to {filename}')


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--num_elements', type=int, default=3, help="Number of unique elements in file")
    parser.add_argument('--size', type=parse_size, default="100 MB", help="Target size for file")
    parser.add_argument('--filename', type=str, default='big_file.txt', help="Output file name")

    args = parser.parse_args()

    main(args.num_elements, args.size, args.filename)

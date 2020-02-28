import argparse

from .importing.fixer import Fixer


def main() -> None:
    Fixer.print_fixed_content(args.file_path)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('file_path', type=str)
    args = parser.parse_args()
    main()

import argparse
import os
import re
import sys

# Not yet implemented
# ただ単に削除したほうがましかもしれないということで作成中止

def main():
    parser = argparse.ArgumentParser(prog='Remove unneccesary exe files except exceptions.txt')
    parser.add_argument('-d',
                        nargs=1,
                        required=True,
                        help="directory")

    args = parser.parse_args()

    dir = args.d[0]


if __name__ == '__main__':
    main()

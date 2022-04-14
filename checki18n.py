
import argparse
from operator import contains
from os.path import exists, isfile, isdir
from tokenize import group
import xml.etree.ElementTree as ET
import os
import re
import sys
import traceback
import logging


def isCppComment(line):
    ''' check line is c++ comment '''
    return re.match('^\\s*//', line)


def getFirstUnquotedString(str):
    str = str.strip()
    if not str:
        return None, None
    if str[0] != '"':
        return None, None

    index = 1
    result = ''
    while True:
        if str[index] == '\\':
            index = index + 1
            result += str[index]
        elif str[index] == '"':
            break
        else:
            result += str[index]
        index = index + 1
        if len(str) <= index:
            return None, None
    return result, index + 1


def getNameAndValueFromI18nLine(i18nline):
    ''' Obtain name and value from i18n line '''
    first, index = getFirstUnquotedString(i18nline)
    if not first or not index:
        return None, None

    # find '='
    while True:
        if i18nline[index] == '"':
            return None, None
        if i18nline[index] == '=':
            index = index + 1
            break
        index = index + 1
        if len(i18nline) <= index:
            return None, None

    second, _ = getFirstUnquotedString(i18nline[index:])
    return first, second


def main():
    parser = argparse.ArgumentParser(prog='check i18n in complete')
    parser.add_argument('-d',
                        nargs=1,
                        required=True,
                        help="directory that contains files")
    parser.add_argument('-r',
                        nargs=1,
                        required=False,
                        help="resource xml")
    parser.add_argument('-t',
                        nargs=1,
                        required=False,
                        help="i18n.txt file")
    parser.add_argument('-m',
                        nargs=1,
                        required=True,
                        help="i18n CppMacro")
    parser.add_argument('-e',
                        action='store_true',
                        help="Shows as entry for i18n.txt")

    args = parser.parse_args()

    dir = args.d[0]
    res = args.r[0] if args.r else None
    i18nt = args.t[0] if args.t else None
    if not res and not i18nt:
        exit("'-r' or '-t' must be specified.")
    if res and i18nt:
        exit("both '-r' and '-t' are specified.")
    macro = args.m[0]

    if not exists(dir):
        exit('{} does not exist'.format(args.d))
    if not isdir(dir):
        exit('{} is not a directory')

    if res:
        if not exists(res):
            exit('{} does not exist'.format(res))
        if not isfile(res):
            exit('{} is not a file'.format(res))
    elif i18nt:
        if not exists(i18nt):
            exit('{} does not exist'.format(i18nt))
        if not isfile(i18nt):
            exit('{} is not a file'.format(i18nt))
    else:
        exit('Unexpected')

    resex = {}
    if res:
        # xmlデータを読み込みます
        tree = ET.parse(res)
        # 一番上の階層の要素を取り出します
        root = tree.getroot()
        for child in root:
            if child.tag != 'data':
                continue
            if not child.attrib['name']:
                continue
            name = child.attrib['name']
            value = child[0].text
            if name:
                resex[name] = value
    elif i18nt:
        with open(i18nt, "r", encoding='utf-8-sig') as i18nFile:
            for i18nline in i18nFile:
                name, value = getNameAndValueFromI18nLine(i18nline)
                if name:
                    resex[name] = value

    else:
        exit('Unexpected.')

    # load from dir
    i18ns = []
    for root, subdirs, filenames in os.walk(dir):
        # print('--\nroot = ' + root)
        for filename in filenames:
            if filename.endswith(".cpp") or filename.endswith(".h"):
                try:
                    with open(os.path.join(root, filename), "r", encoding='utf-8-sig') as file:
                        for line in file:
                            if not isCppComment(line):
                                # TODO: This search can not find the MACRO which contains '\"'
                                match = re.search(
                                    macro + '\s*\(.*\"(([^\\\"]|\\.)*)\"', line)
                                if match:
                                    if match.group(1):
                                        if not match.group(1) in i18ns:
                                            i18ns.append(match.group(1))
                except UnicodeDecodeError as e:
                    if filename.lower() == "resource.h":
                        pass
                    else:
                        logging.error(traceback.format_exc())
                        logging.error(filename)
                except Exception as e:
                    # sys.stderr.write("An exception occurred in " + filename)
                    logging.error(traceback.format_exc())
                    # sys.stderr.write(e)

    nais = []
    for i18n in i18ns:
        if not i18n in resex:
            nais.append(i18n)

    for nai in nais:
        if args.e:
            print('"{}"=""'.format(nai))
        else:
            print(nai)


if __name__ == '__main__':
    main()

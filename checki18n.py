
import argparse
from os.path import exists,isfile,isdir
import xml.etree.ElementTree as ET
import os
import re

def main():
    parser = argparse.ArgumentParser(prog='check i18n in complete')
    parser.add_argument('-d',
                    nargs=1,
                    required=True,
                    help="directory that contains files")
    parser.add_argument('-r',
                    nargs=1,
                    required=True,
                    help="resource xml")

    args = parser.parse_args()

    dir = args.d[0]
    res = args.r[0]

    if not exists(dir):
        exit('{} does not exist'.format(args.d))
    if not isdir(dir):
        exit('{} is not a directory');

    if not exists(res):
        exit('{} does not exist'.format(res))
    if not isfile(res):
        exit('{} is not a file'.format(res))

    #xmlデータを読み込みます
    tree = ET.parse(res)
    #一番上の階層の要素を取り出します
    root = tree.getroot()
    resex = {}
    for child in root:
        if child.tag != 'data':
            continue
        if not child.attrib['name']:
            continue
        name = child.attrib['name']
        value = child[0].text
        if name:
            resex[name] = value

    # load from dir
    i18ns = []
    for root, subdirs, filenames in os.walk(dir):
        # print('--\nroot = ' + root)
        for filename in filenames:
            if filename.endswith(".cpp") or filename.endswith(".h"): 
                with open(os.path.join(root,filename),"r",encoding='utf8') as file:
                    for line in file:
                        # match = re.search('I18N\s*L\s*\"([^\\\"]|\\.)*\"', line)
                        match = re.search('I18N\s*\(.*\"(([^\\\"]|\\.)*)\"', line)
                        if match:
                            if match.group(1):
                                i18ns.append(match.group(1))

    nais = []
    for i18n in i18ns:
        if not i18n in resex:
            nais.append(i18n)

    for nai in nais:
        print(nai)

if  __name__ == '__main__':
    main()
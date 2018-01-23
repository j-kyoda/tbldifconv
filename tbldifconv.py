#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert Thunderbird address ldif to your ldap ldif.
"""
import argparse
import base64
import re


def parse_entry(lines):
    """make entry object

    Arguments:
        lines  -- entry lines

    Returns:
        entry object
    """
    entry = {}
    for line in lines:
        line = line.replace('\n', '').replace('\r', '')
        if ': ' in line:
            (key, value) = line.split(': ')
            if key not in entry:
                entry[key] = []
            entry[key].append(value)
    return entry


def dump_entry(entry, base_path):
    """dump entry

    Arguments:
        entry     -- entry object
        base_path -- ldap base path

    Returns:
        nothing
    """
    if 'mail' not in entry:
        return
    mail = entry['mail'][0]

    # remove attribute if exist
    rm_keys = ['modifytimestamp', 'birthyear', 'birthday']
    for rm_key in rm_keys:
        if rm_key in entry:
            del entry[rm_key]

    # append attribute
    if 'cn' not in entry:
        entry['cn'] = [mail]

    if 'sn' not in entry:
        entry['sn'] = [mail]

    # replace attribute
    if 'dn' in entry:
        entry['dn'] = [f'mail={mail},{base_path}']

    # formatting
    lines = []
    for (key, values) in entry.items():
        for value in values:
            line = f'{key}: {value}'
            lines.append(line)
    lines.append('')

    # output
    for line in lines:
        print(line)


def b64decode(line):
    """decode line

    Arguments:
        line -- Thunerbird address ldif line

    Returns:
        decoded line
    """
    if ':: ' not in line:
        return line
    (key, value) = line.split(':: ')
    _value = base64.b64decode(value).decode('utf-8')
    return f'{key}: {_value}'


def dump(fobj, base_path):
    """split each entry and dump it

    Arguments:
        fobj      -- Thunderbird address ldif file object
        base_path -- ldap base path

    Returns:
        nothing.
    """
    lines = []
    for line in fobj:
        line = line.replace('\n', '').replace('\r', '')
        line = b64decode(line)
        if line:
            lines.append(line)
            continue
        someone = parse_entry(lines)
        dump_entry(someone, base_path)
        lines = []


def main():
    parser = argparse.ArgumentParser(
        description='Convert Thunderbird address ldif to your ldap ldif.')
    parser.add_argument('fname',
                        metavar='FILE',
                        type=argparse.FileType(),
                        help='Thunderbird address ldif')
    parser.add_argument('-b',
                        metavar='BASE_PATH',
                        dest='base_path',
                        required=True,
                        help='ldap base path')

    args = parser.parse_args()
    dump(args.fname, args.base_path)


if __name__ == '__main__':
    main()

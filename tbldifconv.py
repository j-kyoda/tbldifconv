#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert Thunderbird address ldif to your LDAP ldif, or the reverse.
"""
import argparse
import base64
import re


def parse_entry(lines):
    """Read lines and make entry object

    Arguments:
        lines  -- entry lines

    Returns:
        entry object
    """
    entry = {}
    for line in lines:
        line = line.replace('\n', '').replace('\r', '')
        if ':: ' in line:
            (key, value) = line.split(':: ')
            value = base64.b64decode(value).decode('utf-8')
        elif ': ' in line:
            (key, value) = line.split(': ')
        else:
            continue
        if key not in entry:
            entry[key] = []
        entry[key].append(value)
    return entry


def adjust_entry_ldap(entry, base_path):
    """Adjust entry for LDAP

    Arguments:
        entry     -- entry object
        base_path -- ldap base path

    Returns:
        Nothing.
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


def adjust_entry_thunderbird(entry):
    """Adjust entry for Thunderbird

    Arguments:
        entry     -- entry object

    Returns:
        Nothing.
    """
    if 'mail' not in entry:
        return
    mail = entry['mail'][0]

    # append
    if 'modifytimestamp' not in entry:
        entry['modifytimestamp'] = ['0']

    # remove
    if 'cn' in entry:
        if entry['cn'] == mail:
            del entry['cn']

    if 'sn' in entry:
        if entry['sn'] == mail:
            del entry['sn']

    # replace attribute
    if 'dn' in entry:
        if 'cn' in entry:
            cn = entry['cn'][0]
            entry['dn'] = [f"cn={cn},mail={mail}"]
        else:
            entry['dn'] = [f'mail={mail}']


def dump_entry_for_ldap(entry):
    """Dump entry for LDAP ldif

    Arguments:
        entry     -- entry object

    Returns:
        Nothing.
    """
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


def dump_entry_for_thunderbird(entry):
    """Dump entry for Thunderbird ldif

    Arguments:
        entry     -- entry object

    Returns:
        Nothing.
    """
    # formatting
    reg = re.compile('^[-\w\d\s\.@?]+$', flags=re.ASCII)
    lines = []
    for (key, values) in entry.items():
        for value in values:
            need_escape = False
            if key != 'dn':
                if not reg.match(value):
                    need_escape = True
            else:
                if 'cn' in entry:
                    cn = entry['cn'][0]
                    if not reg.match(cn):
                        need_escape = True
            if need_escape:
                b = value.encode('utf-8')
                value_ = base64.b64encode(b).decode('utf-8')
                line = f'{key}:: {value_}'
            else:
                line = f'{key}: {value}'
            lines.append(line)
    lines.append('')

    # output
    for line in lines:
        print(line)


def convert(fobj, base_path=''):
    """Convert ldif

    Arguments:
        fobj      -- Thunderbird ldif file object
        base_path -- ldap base path(when convert to LDAP ldif)

    Returns:
        Nothing.
    """
    lines = []
    for line in fobj:
        line = line.replace('\n', '').replace('\r', '')
        if line:
            lines.append(line)
            continue
        # convert and dump
        someone = parse_entry(lines)
        if base_path:
            # Thunderbird -> LDAP
            adjust_entry_ldap(someone, base_path)
            dump_entry_for_ldap(someone)
        else:
            # LDAP -> Thunderbird
            adjust_entry_thunderbird(someone)
            dump_entry_for_thunderbird(someone)
        lines = []


def main():
    """Main routine

    Parse arguments and call subrouteine.
    """
    parser = argparse.ArgumentParser(
        description='Convert Thunderbird address ldif to your LDAP ldif,'
                    ' or the reverse.')
    parser.add_argument('-b',
                        metavar='BASE_PATH',
                        dest='base_path',
                        default='',
                        help='ldap base path')
    parser.add_argument('-f',
                        metavar='FILE',
                        dest='fname',
                        type=argparse.FileType(),
                        required=True,
                        help='ldif file')

    args = parser.parse_args()
    convert(args.fname, args.base_path)


if __name__ == '__main__':
    main()

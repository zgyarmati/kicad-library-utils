#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from sch import *
import argparse
import csv, sys

parser = argparse.ArgumentParser()
parser.add_argument('sch_file', nargs='+')
parser.add_argument('--bom-csv', help='a BOM csv file that will be used to fill the MPN field', action='store')
parser.add_argument('--bom-ref-field', help='defines the reference field name in the BOM', action='store', default='Reference(s)')
parser.add_argument('--bom-mpn-field', help='defines the Manufacturer PN field name in the BOM', action='store', default='MPN')
args = parser.parse_args()
bom = []

if args.bom_csv:
    f = open(args.bom_csv, 'r')
    reader = csv.reader(f)
    header_ok = False
    for row in reader:
        # Try to locate the header row
        if args.bom_ref_field in row and args.bom_mpn_field in row:
            header_ok = True
            ref_col = row.index(args.bom_ref_field)
            mpn_col = row.index(args.bom_mpn_field)

        elif header_ok:
            bom.append(row)

    if not header_ok:
        sys.stderr.write('Cannot find a header with one or both fields: "%s", "%s"\n' % (args.bom_ref_field, args.bom_mpn_field))
        sys.exit()

for f in args.sch_file:
    sch = Schematic(f)

    for component in sch.components:
        # check if is power related component
        if ('#PWR' in component.fields[0]['ref'] or
            'PWR_FLAG' in component.fields[1]['ref']):
            continue

        # create or get the MPN field
        for field in component.fields:
            if field['name'] == '"MPN"':
                break
        else:
            field = component.addField({'name':'"MPN"', 'ref':'"~"'})

        # component reference
        comp_ref = component.fields[0]['ref'].replace('"','')

        # search the component in the BOM items and get the MPN
        for item in bom:
            item_refs = item[ref_col].replace(' ','').split(',')
            if item[mpn_col] and comp_ref in item_refs:
                field['ref'] = '"' + item[mpn_col] + '"'
                break

    sch.save()

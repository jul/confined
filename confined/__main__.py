#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import
from confined import *
import argparse
from json import dumps, loads
from sys import argv, stdin, exit

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''
Templatize a confined page
==========================

cf https://github.com/jul/confined

If no input file are given use stdin

Example
------

INPUT *************************************************************

cat <<'EOF' | python3 -i -mconfined  -j '{"name" : "jul", "f" : 1}' 
hello my name is <: $name "ie": "n": $f  DUP >NUM IFT  CAT CAT :>
j+1 = <: $f >NUM 1: ADD :>
what if I made a syntax error ? <: 1: 2:
BOOM 3: :>
EOF

OUTPUT ************************************************************

hello my name is julien
j+1 = 2.0
what if I made a syntax error ? 
UNRECOGNIZED TOKEN >BOOM< 
====================
 1: 2: >BOOM<  
===================

*********************************************************************

''')
parser.add_argument('-json', default='',help="json with a dict for the template")
parser.add_argument('file', nargs='?', help='optional file to interpret else use stdin')
res=parser.parse_args()

def usage(status=0):
    parser.print_help()
    exit(status)

try:
    to_read= open(res.file) if res.file else stdin
    print(templatize(loads(res.json), to_read.read()))
except Exception as e:
    print("check arguments")
    print(res)
    print(e)
    usage(1)

"""
print(templatize(dict(name = "super carcajou"), "hellp <: $name :>"))
print(parse(dict(a=1, b=2),'''

+1.23:exist +12:int "AZE":a_string +123:a_number $a $b >NUM SWAP 
"a_string":_key GET "a":another_key
"toto":_miss_get GET CAT "data":_tag TAG  TOP
1:thos 1.2:notavala 3:val 1:_totest 3:sizeo_compare MATCH IFT "FUN":_str
"SWAP,EJOIN":test_eval EVAL "toto":AZE 

'''))
print( templatize(dict(
    price=1, q=3, vat=19.6, name="super carcajou", country="FR"),
'''
<:
"hello":world
:> ici <:
    $name :>

<:
    $price >NUM
    $q >NUM MUL
    $vat >NUM 100:_per_cent_to_per_one DIV 
    1:_having_price_AND_vat ADD MUL >STR
    " ":_separator
    CAT
    "comment in string and drop":_or_in_tag
    DROP
    "€":_cur "$":_cur 
    $country
    "FR":_cocorico
    1:_nb_of_lines_for_looking_match
    MATCH
    IFT
    CAT :>
may I have a dict please? <:
    $price >NUM
    $q
    "a string":with_a_name
    "ignored":_because_tag_starts_with_
    1231231231231231:a_long_int
    "a new name":_with_space
    TAG
    EDICT
:>  ....
<: "fin": :>
'''
))
'''
"""

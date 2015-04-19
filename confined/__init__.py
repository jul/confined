#!/usr/bin/env python
# -*- coding: utf8 -*-
from decimal import Decimal as NUM, getcontext, setcontext, Inexact, Rounded, Context
from operator import mul as MUL, div as DIV, add as ADD, sub as SUB
from string import Template
from functools import wraps

from check_arg import valid_and_doc, default_doc_maker

def must_be_in(whitelist):
    def must_be_in(a):
        if a not in whitelist:
            raise Exception("%r not in whitelist %r" % (a, whitelist))
    return must_be_in

def positional_can_be(*wanted_type):
    def positional_can_be(*arg):
        wanted_ptype= list(wanted_type)
        argl = list(arg)[1:]
        for pos, argu in enumerate(argl):
            if not any(map(lambda pt: isinstance(argu, pt),wanted_ptype[pos] )):
                raise Exception("%r is not of type %r" % (argu, wanted_ptype[pos]))
    return positional_can_be

def last_types_in_stack_must_be(*wanted_type):
    def last_types_in_stack_must_be(*arg):
        a = list(arg[-1])
        for i, type in enumerate(reversed(wanted_type)):
            i+=1
            if a[-i].type != type:
                raise Exception("%s is not of type %s" % (a[-i], type))
    return last_types_in_stack_must_be


check_type = valid_and_doc(last_types_in_stack_must_be)
can_be = valid_and_doc(positional_can_be)
whitelist = valid_and_doc(must_be_in)

def must_return_value(f):
    @wraps(f)
    def check_f(*a, **kw):
        res= f(*a,**kw)
        assert isinstance(res, Value), "%r is not of type Value" % res
        return res
    return check_f
# Reverse Polish Notation calculator
# based on http://en.wikipedia.org/wiki/Reverse_Polish_notation
ctx = getcontext()

dispatch_op = dict( 
    MUL = MUL, DIV=DIV, ADD=ADD, SUB=SUB
)
def pop(n):
    def fr(stack):
        return [ stack.pop() for i in range(n) ]
    return fr
def pop_val(n):
    def fr(stack):
        return [ stack.pop().val for i in range(n) ]
    return fr
def is_int(decimal):
    try:
        decimal.to_integral_exact(Context(traps=[Inexact, Rounded]))
        return True
    except:
        return False
class Value(object):
    prec = 2
    encoding="utf8"
    @can_be({str,unicode,NUM}, {str}) 
    def __init__(self, val, tag=''):
        self.tag, self.val= tag, val
    @property
    def type(self):
        return isinstance(self.val, NUM) and "num" or "str"

    @property
    def int(self):
        assert self.type=="num"
        return int(self.val.to_integral_value())

    @property
    def is_int(self):
        assert self.type=="num"
        return is_int(self.val)
        

    @property
    def _out(self):
        return dict(
            str = str,
            num = lambda v:str(int(self.val) if is_int(self.val) else
float(v.quantize(NUM(10) ** -Value.prec))),
        )[self.type](self.val)
    @property
    def str(self):
        return self._out.decode(Value.encoding) if self.type == "str" else str(self._out)
    def __repr__(self):
        return "".join(["<Val:type='", self.type,"' val=",self._out[:10] +
( len(self._out)>10 and "..." or "")," tag='%(tag)s'>" % (self.__dict__)])

N,V = NUM, Value

@check_type("str")
def to_num(stack):
    """Convert the last element of the stack from a string to a num"""
    value = stack[-1]
    value.val = N(value.val)
@check_type("num")
def to_str(stack):
    """Convert the last element of the stack from a string to a num"""
    value = stack[-1]
    value.val = value.val.str

true, false = Value(N(1), "_true"), Value(N(0), "_false")

def to_dict(stack):
    """convert a stack to a dict"""
    return { v.tag: v._out for v in stack if not v.tag.startswith("_") }

@check_type("num")
def ift(stack):
    """ If then else expects in the stack
    2: value_true
    1: value_false
    0: test
    return value_true if test else value_false
    """
    true, false, val = reversed(pop(3)(stack))
    stack+= [ true if bool(val.val) else false ]

@check_type("num")
def match(stack):
    """tells how much time an the reference has match any of the n value above
    consumes all the elements, leaves the number of match on the stack

     ... matchable
     ...   matchable
     2: matchable
     1: reference
     0: iter 
     --------------
    => 0: V(N(matches), "_matches")
    """
    iter, ref = pop(2)(stack)
    iter = iter.int
    matches = 0
    to_compare = pop(iter)(stack)
    for to_comp in to_compare:
        if to_comp.type != ref.type:
            raise ValueError("%r is not the same type as %r" % (ref, to_comp))
        if to_comp.val == ref.val:
            matches += 1
    stack+=[ Value(N(matches), "_matches") ]

@check_type("str", "num", "num")
def splice(stack):
    """
    """
    value, _start, _stop = reversed(pop(3)(stack))
    value.val = value.val[_start.int:_stop.int]
    stack += [ value ]

@whitelist(dispatch_op.keys())
def num_op(op):
    @check_type("num", "num")
    def do_op(stack):
        stack += [ Value(NUM(dispatch_op[op](*pop_val(2)(stack)))) ]
    return do_op

@check_type("str", "str")
def cat(stack):
    stack+= [ Value("".join(pop_val(2)(stack))) ]

@check_type("str")
def tag(stack):
    """ give the tag name to the last value
    1: value
    0: tag
    => 0: value.tag = tag.value
    """
    tag, val = pop(2)(stack)
    val.tag = tag.val
    stack += [ val ]
def display(stack):
    print "******************************************"
    for i, v in enumerate(stack):
        rel = len(stack)
        print "| %3d | %r" % (rel - i -1, v) 
    print "******************************************"

def top(stack):
    stack.insert(0,stack.pop())


@check_type("str")
def get(stack):
    pos = -1
    key = pop_val(1)(stack).pop()
    found = False
    while not found and abs(pos) <= len(stack):
        if str(stack[pos].tag) == str(key):
            found = True
        pos -= 1
    if found:
        stack += [ V(N((abs(pos)-1)), "_findex") ]
        display(stack)
        rotn(stack)

@check_type("num")
def rotn(stack):
    rpos = -(stack.pop().int)
    assert rpos<-1
    assert len(stack)>abs(rpos+1)
    pivot = stack[rpos]
    stack[rpos:] = stack[rpos+1:]
    stack += [ pivot  ]

def swap(stack):
    stack[-2], stack[-1] = stack[-1], stack[-2] 

def drop(stack):
    stack.pop()

def dup(stack):
    stack += stack[-1]
def leng(stack):
    stack += [ V(N(len(stack)),"_length") ]

import math
@check_type("str")
def eval(stack):
    parse({}, stack.pop().str.replace(",", " "), stack)

def ejoin(stack):
    print "EXITING"
    stack += [ "&".join([ "=".join([v.tag,v.str]) for v in stack if not
v.tag.startswith("_") and v.tag ]),  "<<TERM>>" ]
import operator
def edict(stack):
    print "EXITING"
    stack+=[ to_dict(stack), "<<TERM>>" ]

ops = { name : num_op(name) for name in dispatch_op }
ops.update({
       ">NUM" : to_num,
       ">STR" : to_str,
       "CAT" : cat,
       "TAG" : tag,
       "IFT" : ift,
       "MATCH" : match,
       "ROT" : rotn,
       "DUP" : dup,
        "TOP" : top,
       "DROP" : drop,
       "SWAP" : swap,
       "GET" : get,
       "LEN" : leng,
       "EJOIN" : ejoin,
        "EDICT" : edict,
       "EVAL" : eval,
       "<<TERM>>" : lambda x:x,
      
})
import re
base_type = dict(
    num = '''[+-]?((?=\d*[.eE])(?=\.?\d)\d*\.?\d*(?:[eE][+-]?\d+)?|\d+)''',
    dqstring = r'''"[^"\\]*(?:\\[\S\s][^"\\]*)*"''',
    sqtring = r"""'[^'\\]*(?:\\[\S\s][^'\\]*)*'""",
    string = r'''(%(sqtring)s|%(dqstring)s)''',
    id = "([a-z]|_)?(?:[a-z0-9_]*)",
    VOID = "^(\s+)$"
)
parse_base = { k:re.compile(v % base_type, re.I|re.M|re.VERBOSE).match for k,v in
base_type.items() }


def get_string(expr):
    res = parse_base["string"](expr)
    if res:
        return res.group()[1:-1]


def tokenize(ops,str):
    atom = dict(
        ALL = r"""(%(STR)s|%(NUM)s|%(OP)s|%(VAR)s)""",
        STR = '''(?P<STR>(%(dqstring)s|%(sqtring)s):%(id)s)''',
        NUM = '''(?P<NUM>%(num)s:%(id)s)''',
        OP = "(?P<OP>%s)" % "|".join(ops.keys()),
        VAR = r"""(?P<VAR>\$\S+)""",
    )
    regexp = re.compile(r"""%(ALL)s""" % atom % atom % base_type  ,
        re.MULTILINE|re.VERBOSE|re.I)
    return regexp.finditer(str)

def parse(ctx, string, data=[]):
    res = None
    last_match=0
    current_match=0
    cur_pos = 0
    last_token = 0 
    Value.encoding="utf8"
    try:
        for i,kwd in enumerate(tokenize(ops, string)):
            last_unrecognized = string[last_match:kwd.start()]
            last_token = kwd.end()
            if last_unrecognized and not parse_base["VOID"](last_unrecognized):
                toprint=string[0:last_match] + "<%s>" % last_unrecognized + \
                    string[kwd.end():]
                raise Exception("Un parsed expression **%s** in %s" %
                    (last_unrecognized, toprint))
            cur_pos, current_match = current_match, kwd.start()
            old,last_match = last_match, kwd.end()
            kwd = kwd.groupdict()
            if len(data)>2 and "<<TERM>>" == data[-1]:
                # TERM of the code is either end of string
                # or an OP dumping <<TERM>> and a res in stack
                data.pop()
                res= data.pop()
                break
            if kwd["OP"]:
                # balck magic
                print "BEFORE APPLYING %d, %s" %(i, kwd["OP"])
                display(data)
                ops[kwd["OP"]](data)
                print "AFTER %(OP)s" % kwd
                display(data)
                print
            if kwd["NUM"]:
                # no : in num regexp, so I can do it
                val, tag = kwd["NUM"].split(":")
                data+= [ V(N(val), tag.strip()) ]
            if kwd["STR"]:
                #tag dont match string so I can do it
                tag = kwd["STR"].split(":")[-1]
                data+= [ V(get_string(kwd["STR"]), tag.strip()) ]
            if kwd["VAR"]:
                # dont use "safe_substitute" it is unsafe
                data+= [ V(Template(kwd["VAR"],).substitute(ctx), kwd["VAR"][1:]) ]
    except Exception as e:
        before = string[:current_match]
        current = string[current_match:last_token]
        after = string[last_token:]
        toprint= "**".join([before, current, after])
        print toprint
        print "<%s> triggered EXCP %s" % (current.strip(), e)
    display( data )
    if res:
        from json import dumps
        print dumps(to_dict(data), indent=4)
        return res

print parse(dict(a=1, b=2),'''

"accentué":accent +1.23:exist +12:int "AZE":a_string +123:a_number $a $b >NUM SWAP 
"a_string":_key GET "a":another_key
"toto":_miss_get GET CAT "data":_tag TAG  TOP
1:thos 1.2:notavala 3:val 1:_totest 3:sizeo_compare MATCH IFT "FUN":_str
"SWAP,EJOIN":test_eval EVAL "toto":AZE 

''')
print parse(dict(a=1, b=2),'''

+1.23:exist syntax_error_lololol +12:int "AZE":a_string +123:a_number $a $b >NUM SWAP 
"a_string":_key GET "a":another_key
"toto":_miss_get GET CAT "data":_tag TAG  TOP
1:thos 1.2:notavala 3:val 1:_totest 3:sizeo_compare MATCH IFT "FUN":_str
"SWAP,EJOIN:test_eval EVAL "toto":AZE 

''')

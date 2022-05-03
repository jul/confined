#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import
from typing import Final
import re
from decimal import Decimal as NUM, getcontext, setcontext, Inexact, Rounded, Context
from json import dumps
from string import Template
from sys import stderr
from functools import wraps

from .check_arg import valid_and_doc, default_doc_maker

class TerminalException(Exception):
    pass

def must_be_in(whitelist, whitelist_type="operators"):
    def must_be_in(a):
        if a not in whitelist:
            raise Exception("%r not in whitelist %r" % (a, whitelist))
    return must_be_in

def positional_can_be(*wanted_type):
    def positional_can_be(*arg):
        wanted_ptype= list(wanted_type)
        argl = arg[1:]
        message = []
        for pos, argu in enumerate(argl):
            if not any(map(lambda pt: isinstance(argu, pt),wanted_ptype[pos] )):
                raise Exception("TypeCheck::%r (pos %d) is not of type %r" % (argu._out,pos,wanted_ptype[pos]))
    return positional_can_be


def last_types_in_stack_must_be(*wanted_type):
    def last_types_in_stack_must_be(stack):
        message = []
        to_highlight= []
        for i, _type in enumerate(reversed(wanted_type)):
            i += 1
            if stack[-i].type != _type:
                message += ["(%r) (new pos %d) %s is not of type %s" % (stack[-i],i, stack[-i].type,_type) ]
                to_highlight += [ len(stack) -  i,]
        if message:
            conf_error(stack, "TypeCheck", message, highlight=to_highlight)
        if message: raise Exception("CONFINED ERROR :Checking Types")
    return last_types_in_stack_must_be

def min_stack_size(size):
    def min_stack_size(stack):
        if len(stack)<size:
            conf_error(
                stack, 
                "StackUnderflow",
                "For this operation stack expected to be (%d) and is %d" % (size,len(stack))
            )
            raise Exception("CONFINED ERROR:Stack is too small %d argument required, stack has %d element" % (size,len(stack)))
    return min_stack_size

min_stack = valid_and_doc(min_stack_size)
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


class Value(object):
    prec = 2
    encoding="utf8"

    @can_be({str,NUM}, {str})
    def __init__(self, val, tag=''):
        self.tag, self.val= tag, val

    def copy(self):
        val = self.val
        return Value(N(val) if self.type == "num" else val ,self.tag)

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
        ### this is ugly TODO : rewrite
        return dict(
            str = str,
            num = lambda v: str(int(self.val) if is_int(self.val) else
                #float(v.quantize(NUM(10) ** -Value.prec))),
                float(v)),
        )[self.type](self.val)

    @property
    def str(self):
        return str(self._out)

    def __repr__(self):
        quote = self.type == "str" and '"' or ""
        return "".join([quote, self._out,quote, ":%(tag)s" % (self.__dict__)])

N,V = NUM, Value
#true, false = V(N(1),"true"), V(N(0), "false")
true : Final= V(N(1),"true")
false:Final = V(N(0), "false")

def display(stack, highlight=set({})):
    """TODO : use the context with log to compute the %xd"""
    print ("******************************************")
    for i, v in enumerate(stack):
        high = str(v)
        if i in set(highlight): high = ">%s<" % high
        rel = len(stack)
        print( "| %3d | %s " % (rel - i -1, high))
    print ("******************************************")


def conf_error(stack,error_type, error_msgs, highlight=set({})):
    
    print(error_type)
    display(stack, highlight=highlight)
    stack += [ V("\nType: >%s< \n====================\n%s\n===================\n" % (error_type, "".join(error_msgs)), "ERROR") ]

dispatch_op = dict(
)

def pop(n):
    @min_stack(n)
    def fr(stack):
        return [ stack.pop() for i in range(n) ]
    return fr

def pop_val(n):
    @min_stack(n)
    def fr(stack):
        return [ stack.pop().val for i in range(n) ]
    return min_stack(n)(fr)

def is_int(decimal):
    try:
        decimal.to_integral_exact(Context(traps=[Inexact, Rounded]))
        return True
    except:
        return False


@min_stack(1)
@check_type("str")
def to_num(stack):
    """Convert the last element of the stack from a string to a num"""
    value = stack[-1]
    value.val = N(value.val)

@min_stack(1)
@check_type("num")
def to_str(stack):
    """Convert the last element of the stack from a a num to a string"""
    n = stack.pop()
    stack += [ V(n.str,n.tag)]

#true, false = Value(N(1), "_true"), Value(N(0), "_false")

def to_dict(stack):
    """convert a stack to a dict"""
    return { v.tag: v._out for v in stack if v.tag and not v.tag[0] == ("_") }

@min_stack(3)
@check_type("num")
def ift(stack):
    """ If then else expects in the stack
    2: value_true
    1: value_false
    0: test
    return value_true if test else value_false
    """
    true, false, val = reversed(pop(3)(stack))
    stack += [ true if bool(val.val) else false ]

@check_type("num")
def match_tag(stack):
    """tells how much time an the reference has match any of the n value above
    consumes all the elements, leaves the number of match on the stack

     ... matchable
     ... matchable
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
        if to_comp.tag == ref.tag:
            matches += 1
    stack += [ Value(N(matches), "_tag_matches") ]

@check_type("num")
def match(stack):
    """tells how much time an the reference has match any of the n value above
    consumes all the elements, leaves the number of match on the stack

     ... matchable
     ... matchable
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
    stack += [ Value(N(matches), "_matches") ]
@min_stack(3)
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


@min_stack(2)
@check_type("str", "str")
def cat(stack):
    v1, v2 =pop(2)(stack)
    stack+= [ Value(v2.val+v1.val,v1.tag) ]

@min_stack(2)
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

@min_stack(1)
def top(stack):
    """use the top of the stack as a stack where to put/fetch stuff"""
    stack.insert(0,stack.pop())

@min_stack(1)
@check_type("str")
def get(stack):
    """find element matching tag of the last value on the stack
    emulate a dict.get behaviour
    """
    pos = -1
    key = pop_val(1)(stack).pop()
    found = False
    while not found and abs(pos) <= len(stack):
        if str(stack[pos].tag) == str(key):
            found = True
        pos -= 1
    if found:
        stack += [ V(N((abs(pos)-1)), "_findex") ]
        rotn(stack)

@min_stack(2)
@check_type("num")
def rotn(stack):
    """
    pick the nth element in the stack
    """
    rpos = -(stack.pop().int)
    assert rpos<-1
    assert len(stack)>abs(rpos+1)
    pivot = stack[rpos]
    stack[rpos:] = stack[rpos+1:]
    stack += [ pivot  ]

def nop(stack):
    pass

@min_stack(2)
def swap(stack):
    """ a b => b a """
    stack[-1], stack[-2] = stack[-2], stack[-1]

@min_stack(2)
def over(stack):
    """ a b OVER => a b a """
    stack += [ stack[-2], ]

@min_stack(1)
def drop(stack):
    """ ... x DROP => ... """
    stack.pop()

@min_stack(1)
def dup(stack):
    """
    .... a DUP => ... a a
    """
    stack += [ stack[-1].copy() ]

def leng(stack):
    """return the size of the stack
    """
    stack += [ V(N(len(stack)),"_length") ]

@min_stack(1)
@check_type("str")
def eval(stack):
    """Eval a string on the stack that is a serie of comma separated operators
    """
    parse({}, stack.pop().str.replace(",", " "), stack)

def ejoin(stack):
    """
    leaves the interpreter and return a join string of all the arguments
    """
    print( "EXITING")
    stack += [ "&".join([ "=".join([v.tag,v.str]) for v in stack if not
        v.tag.startswith("_") and v.tag != "" ]),  "<<TERM>>" ]

def edict(stack):
    print( "EXITING")
    stack+=[ to_dict(stack), "<<TERM>>" ]

two_num = check_type("num", "num")
one_num = check_type("num")

def apply_(f, consume=2, chek_input=two_num, check_output=last_types_in_stack_must_be("num"),**kw):
    """Convenience function to apply f(S[-1], [-2], ...) and push it on stack
    """
    def do(stack):
       
        tag=stack[-1].tag if kw.get("keep_tag", False) else ''
        stack += [V(N(f(*reversed(pop_val(consume)(stack)))),tag)]
        check_output(stack)

    return chek_input(do)

@min_stack(1)
@check_type("num")
def not_(stack):
    """Logical Not"""
    l = stack[-1]
    #if l.tag:
    #    l.val = (N(1),N(0))[bool(l.val)]
    #else:
    stack[-1] = (true, false)[l.val>0]


@min_stack(1)
def val_type(stack):
    v, = pop(1)(stack)
    try:
        stack += [ V(v.type, "type") ]
    except Exception as e:
        stack += [ V("external") ]
@min_stack(1)
@check_type("num")
def ndup(stack):
    v, = pop(1)(stack)
    min_stack_size(v.int)(stack)
    for i in range(len(stack) - v.int,len(stack)):
        stack += [ stack[i].copy(), ]

@min_stack(2)
@check_type("str", "str")
def in_(stack):
    """Find a needle in a haystack"""
    needle, haystack = pop_val(2)(stack)
    stack += [ true if int(needle in haystack) else false ]

@min_stack(2)
@check_type("str", "str")
def string_equal(stack):
    val1, val2 = pop_val(2)(stack)
    stack += [ true if val1==val2 else false ]


@min_stack(2)
@check_type("num", "num")
def cmp_(stack):
    val1, val2 = pop_val(2)(stack)
    stack += [ true if (bool(val1) or bool(val2)) else false ]

@min_stack(2)
@check_type()
def or_(stack):
    val1, val2 = pop_val(2)(stack)
    stack += [ true if (bool(val1) or bool(val2)) else false ]

@min_stack(2)
@check_type()
def and_(stack):
    val1, val2 = pop_val(2)(stack)
    stack += [ true if (bool(val1) and bool(val2)) else false ]

ops = { name : num_op(name) for name in dispatch_op }
ops.update({
       ">NUM" : to_num,
       ">STR" : to_str,
       "CAT" : cat,

       "ADD" : apply_(lambda x,y: N(x + y), keep_tag=True),
       "SUB" : apply_(lambda x,y: N(x - y), keep_tag=True),
       "MUL" : apply_(lambda x,y: N(x * y), keep_tag=True),
       "DIV" : apply_(lambda x,y: N(x / y), keep_tag=True),
       "TRUEDIV" : apply_(lambda x,y: N(x // y)),
       "BXOR" : apply_(lambda x,y: N(int(x) ^ int(y))),
       "BOR" : apply_(lambda x,y: N(int(x) | int(y))),
       "BAND" : apply_(lambda x,y: N(int(x) & int(y))),
       "MOD" : apply_(lambda x,y: N(int(x) % int(y))),
       "CMP" : apply_(lambda x,y: N(x.compare(y)), keep_tag=False),
       "STREQ" : string_equal,
       "TYP" : val_type,
       "IN" : in_,
       "NOT" : not_,
       "OR" : or_,
       "AND" : and_,
       "TAG" : tag,
       "IFT" : ift,
       "MATCH" : match,
       "MTAG" : match_tag,
       "ROT" : rotn,
       "DUP" : dup,
       "NDUP" : ndup,
       "TOP" : top,
       "DROP" : drop,
       "SWAP" : swap,
       "OVER" : over,
       "NOP" : nop,
       "GET" : get,
       "LEN" : leng,
       "EJOIN" : ejoin,
       "EDICT" : edict,
       "EVAL" : eval,
       "<<TERM>>" : lambda x:x,
})
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


def templatize(val,a_str,**kw):
    #pat = re.compile(r'''(?P<CODE><:(((?!(:>|%(string)s)).)*):>)''' %
    pat = re.compile(r'''(?P<CODE><:(((?!(:>)).)*):>)''' %
        base_type % base_type,re.DOTALL|re.VERBOSE)
    tkr = pat.finditer
    build = ""
    last_start_token = 0
    last_end_token = 0
    first=True
    for place in tkr(a_str):
        if first:
            first = False
            build+=a_str[:place.start()]
        if last_end_token != last_start_token:
            build += a_str[last_end_token:place.start()]
        code = place.group()[2:-2]
        res = parse(val, code,[])
        build += res._out if isinstance(res,Value) else dumps(res,indent=4)
        last_end_token = place.end()
    build += a_str[last_end_token:]
    return build

def tokenize(ops,str):
    atom = dict(
        ALL = r"""(%(STR)s|%(NUM)s|%(OP)s|%(VAR)s)""",
        STR = '''(?P<STR>(%(dqstring)s|%(sqtring)s):%(id)s)''',
        NUM = '''(?P<NUM>%(num)s:%(id)s)''',
        OP = "(?P<OP>%s)" % "|".join(ops.keys()),
        VAR = r"""(?P<VAR>\$\S+)""",
    )
    regexp = re.compile(r"""%(ALL)s""" % atom % atom % base_type  ,
        re.MULTILINE|re.VERBOSE)
    return regexp.finditer(str)

_SENTINEL = object()
MAX_STACK=64
def parse(ctx, string, data=_SENTINEL, dbg=False, context=_SENTINEL):
    if context is _SENTINEL:
        context = dict(_max_stack=MAX_STACK, control=False)
    if data is _SENTINEL:
        # fix weired bug in ipython where stack is not destroyed
        data = []
    res = None
    last_match=0
    current_match=0
    cur_pos = 0
    last_token = 0
    Value.encoding="utf8"
    #dbg and data and display(data)
    last_unrecognized=""
    toprint=""
    terminate = context.get("control",False) is False and len(data) > context.get("_max_stack", MAX_STACK)
    
    if terminate: return data[-1]
    try:
        seen=False
        for i,match_kwd in enumerate(tokenize(ops, string)):
            seen=True
            kwd=match_kwd
            last_unrecognized = string[last_match:match_kwd.start()].strip()
            last_token = match_kwd.end()
            if last_unrecognized:
                # BUG DOES NOT SEE LAST SYNTAX ERROR IN FILE (ignored)
                toprint="*%s* in \n" % last_unrecognized + \
                    string[match_kwd.pos:]
                conf_error(data, "UnrecognizedToken", toprint)
                print("\n")
            cur_pos, current_match = current_match, match_kwd.start()
            old,last_match = last_match, match_kwd.end()

            kwd = kwd.groupdict()
            if kwd["OP"]:
                try:
                    ops[kwd["OP"]](data)
                except Exception as e:
                    print(e, file=stderr)
            if len(data)>2 and "<<TERM>>" == data[-1]:
                # TERM of the code is either end of string
                # or an OP dumping <<TERM>> and a res in stack
                data.pop()
                return data[-1]
            if kwd["NUM"]:
                val, tag = kwd["NUM"].split(":")
                try:
                    data+= [ V(N(val), tag.strip()) ]
                except decimal.InvalidOperation:
                    data+=[V("\nInvalidDecimal >%s< \n====================\n%s\n===================\n" % (val), "RepresentationError")]
            if kwd["STR"]:
                #tag dont match string so I can do it
                tag = kwd["STR"].split(":")[-1]
                data+= [ V(get_string(kwd["STR"]), tag.strip()) ]
            if kwd["VAR"]:
                # dont use "safe_substitute" it is unsafe
                data+= [ V(Template(kwd["VAR"],).substitute(ctx), kwd["VAR"][1:]) ]
            dbg and display(data)
            if not context.get("control",False):
                stack_overflow = parse(
                    context,
                    """LEN $_max_stack >NUM 1: SUB CMP NOT NOT """,
                    data=data.copy(),
                    context=dict(control=True)
                )
                if(stack_overflow is true):
                    if(not data[-1].tag.strip().startswith("Type: >Ressource<")):
                        conf_error(data, "Ressource", "limit of stack used")
                    raise(TerminalException("RessourceError: Max stack achieved"))
        if seen is False and string.strip():
            conf_error(data, "UnrecognizedTokenB", string)
        elif last_match+1 < len(string):
            conf_error(data, "UnrecognizedTokenE", string[last_match:])
            
        if not res:
            res = data[-1] if len(data) else "empty"
        return res
    except TerminalException as te:
       terminate = True
       return data[-1]

    except Exception as e:
        import sys, traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        before = string[:current_match]
        current = string[current_match:last_token]
        after = string[last_token:]
        toprint= "**".join([before, current, after])
        toprint+= "".join(traceback.format_tb(exc_traceback))
        toprint+= "<%s> triggered EXCP %s" % (current.strip(), e)

        conf_error(data,"Parsing", toprint )
        return data[-1]

        
    finally:
        del(data)

def console():
    stack = []
# minimal version
#while(s:= input('CONF> ')):
#    if s.strip().lower() in { "quit", "bye", "exit","q", "\q" }:
#        break
#    parse({},s,data=stack, dbg=True)

    from prompt_toolkit import prompt
    from prompt_toolkit.shortcuts import clear
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.completion import WordCompleter
    s=" "
    while 1:
        clear()
        if len(s.strip()) and s.strip().lower() in { "cls" }:
            continue
        if len(s.strip()) and s.strip().lower() in { "quit", "bye", "exit","q", "\q" }:
            break
        res=parse({},s,data=stack, dbg=True)
        if isinstance(res, Value) and not res.tag=="ERROR":
            print("r>" + str(res))
        if isinstance(res, Value) and res.tag=="ERROR" and "Type: >Ressource<" in res.val:
            break
        if stack:
            check_last=[ stack[-1], ]
            r=parse({},"""
                DUP 
                TYP "num": STREQ
                SWAP
                TYP "str": STREQ
                OR""",data=check_last, context=dict(control=True))
            if r is false:
                print(dumps(stack.pop(), indent=4))

        s = prompt(u'CONF# ',
                            history=FileHistory('confined.txt'),
                            completer=WordCompleter(ops.keys()),
                            complete_while_typing=True,
                            )

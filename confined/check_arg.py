#!/usr/bin/env python
# -*- coding: utf8 -*-
__all__ = [ 'default_doc_maker', 'valid_and_doc',]


def default_doc_maker(a_func, *pos, **opt):
    doc = "\n\n%s:%s" % (a_func, a_func.__doc__)
    posd= "%s\n" % ",".join(map(str, pos))  if len(pos)  else ""
    named = "\n%s" % ",\n".join([ "* params: %s is %r"%(k,v) for k,v in opt.items() ]
        ) if len(opt) else ""

    return """
**%s** :%s
%s""" % (
        a_func.__name__,
        posd,
        named
    )

def valid_and_doc(validate, doc_maker = default_doc_maker):
    def wraps(*pos, **named):
        additionnal_doc = doc_maker(validate, *pos, **named)
        def wrap(func):
            def rewrapped(*a,**kw):
                validate(*pos,**named)(*a,**kw)
                return func(*a,**kw)
            rewrapped.__module__ = func.__module__
            rewrapped.__doc__= ( func.__doc__ or "" ) + additionnal_doc
            rewrapped.__name__ = func.__name__
            return rewrapped
        return wrap
    return wraps





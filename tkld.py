# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Pengkui Luo <pengkui.luo@gmail.com>
# Updated 6/19/2013
#
# This module was modified based on the same file in package publicsuffix-1.0.2
# http://pypi.python.org/pypi/publicsuffix
#
# Redistributed under MIT license.
#
# Copyright (c) 2011 Tomaz Solc <tomaz.solc@tablix.org>
#
# Python module included in this distribution is based on the code downloaded
# from http://code.google.com/p/python-public-suffix-list/, which is
# available under the following license:
#
# Copyright (c) 2009 David Wilson
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
# The Public Suffix List included in this distribution has been downloaded
# from http://publicsuffix.org/ and is covered by a separate license. Please
# see the license block at the top of the file itself.

__all__ = [
    'get_t2ld',
    'get_sld_tld',
    'get_t3ld',
    'is_fqdn',
]
print('Executing %s' %  __file__)

import codecs
from os.path import join, dirname

#-----------------------------------------------------------------------------
# Parses public suffix list, and build the tree structure
#
# input_file is a file object or another iterable that returns
# lines of a public suffix list file. If input_file is None, an
# UTF-8 encoded file named "publicsuffix.txt" in the same
# directory as this Python module is used.
# The file format is described at http://publicsuffix.org/list/
#-----------------------------------------------------------------------------

# Two key data containers
Root = [0]
Domain_to_t2ld_cache = {}

def _find_node (parent, parts):
    if not parts:
        return parent
    if len(parent) == 1:
        parent.append({})
    assert len(parent) == 2
    negate, children = parent
    child = parts.pop()
    child_node = children.get(child, None)
    if not child_node:
        children[child] = child_node = [0]
    return _find_node(child_node, parts)

def _add_rule (root, rule):
    if rule.startswith('!'):
        negate = 1
        rule = rule[1:]
    else:
        negate = 0
    parts = rule.split('.')
    _find_node(root, parts)[0] = negate

PATH = join(dirname(__file__), '@data')
with codecs.open(join(PATH, 'effective_tld_names.@r.txt'), 'r', 'utf8') as fr:
    for line in fr:
        line = line.strip()
        if line.startswith('//') or not line:
            continue
        _add_rule (Root, line.split()[0].lstrip('.'))  # Root is changed

def _simplify (node):
    if len(node) == 1:
        return node[0]
    return node[0], {k: _simplify(v) for k,v in node[1].items()}

Root = _simplify (Root)


#-----------------------------------------------------------------------------
# Lookup functions
#-----------------------------------------------------------------------------

def _lookup_node (matches, depth, parent, parts):
    if parent in (0, 1):
        negate = parent
        children = None
    else:
        negate, children = parent
    matches[-depth] = negate
    if depth < len(parts) and children:
        for name in ('*', parts[-depth]):
            child = children.get(name, None)
            if child is not None:
                _lookup_node (matches, depth+1, child, parts)

def get_t2ld (domain):
    """i.e. T2LD, e.g. "www.example.com" -> "example.com"
    and also return TLD if get_tld=True.

    Calling this function with a DNS name will return the
    public suffix for that name.

    Note that if the input does not contain a valid TLD,
    e.g. "xxx.residential.fw" in which "fw" is not a valid TLD,
    the returned public suffix will be "fw", and TLD will be empty

    Note that for internationalized domains the list at
    http://publicsuffix.org uses decoded names, so it is
    up to the caller to decode any Punycode-encoded names.

    """
    global Root, Domain_to_t2ld_cache
    try:
        return Domain_to_t2ld_cache [domain]
    except KeyError:
        parts = domain.lower().lstrip('.').split('.')
        hits = [None] * len(parts)
        _lookup_node (hits, 1, Root, parts)
        for i, what in enumerate(hits):
            if what is not None and what == 0:
                t2ld = '.'.join(parts[i:])
                Domain_to_t2ld_cache [domain] = t2ld
                return t2ld

def get_sld_tld (domain, t2ld=None):
    if t2ld is None:
        t2ld = get_t2ld (domain)
    t2s = t2ld.split('.')
    sld = t2s[0]
    tld = '.'.join(t2s[1:])
    return sld, tld

def get_t3ld (domain, t2ld=None):
    if t2ld is None:
        t2ld = get_t2ld (domain)
    if len(t2ld) == len(domain):
        t3ld = t2ld
    else:
        remains = domain[:-len(t2ld)-1].split('.')  # e.g. ['a','b']
        t3ld = '.'.join([remains[-1], t2ld])
    return t3ld

def is_fqdn (domain):
    """Whether the input domain is a FQDN, i.e. ending with a valid TLD."""
    _, tld = get_sld_tld (domain)
    return tld != ''

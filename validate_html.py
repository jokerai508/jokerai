# -*- coding: utf-8 -*-
"""Validate HTML well-formedness."""
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.void = {'meta', 'link', 'br', 'img', 'hr', 'input', 'source', 'wbr', 'area', 'base', 'col'}
    def handle_starttag(self, tag, attrs):
        if tag not in self.void:
            self.stack.append((tag, self.getpos()))
    def handle_endtag(self, tag):
        if tag in self.void:
            return
        if not self.stack:
            self.errors.append("stray </%s> at %s" % (tag, self.getpos()))
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.errors.append("mismatch: expected </%s> got </%s> at %s" % (self.stack[-1][0], tag, self.getpos()))

p = P()
p.feed(open("/Users/btm6/jokerai/price-alert.html", encoding="utf-8").read())
print("unclosed:", [t for t, _ in p.stack] if p.stack else "none")
print("errors:", p.errors[:5] if p.errors else "none")
print("balanced:", p.stack == [])

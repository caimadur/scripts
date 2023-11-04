#!/usr/bin/env python

"""
Building web pages from Markdown documents.
The conversion is done by markdown2 https://github.com/trentm/python-markdown2
"""


import argparse, markdown2
from contextlib import redirect_stdout
from os.path import exists
from tkinter import messagebox


class Setup:
    indent = 4
    charset = 'utf-8'
    meta = {'viewport': 'width=device-width, initial-scale=1.0',
             'title': "untitled",
             'author': None,
             'description': None,
             'generator': "mdconv.py",
             'keywords': None,
             'robots': None}
setup=Setup()

class Node:
    """Class for HTML nodes"""
    def __init__(self, tag, attributes={}, content=None):
        self.tag = tag
        self.attributes = attributes
        if content:
            self.content = content
        else:
            self.content = []

    def add_content(self, c):
        self.content.append(c)

    def add_attribute(self, a, val):
        self.attributes[a] = val

    def print_html(self, depth=0):
        line = depth * setup.indent * ' ' + '<' + self.tag
        for k, v in self.attributes.items():
            line += ' {0}="{1}"'.format(k, v)
        line += '>'
        if not self.content:
            print(line)
            return
        if len(self.content) == 1 and isinstance(self.content[0], str):
            line += self.content[0]
        else:
            print(line)
            line = depth * setup.indent * ' '
            for i in self.content:
                if isinstance(i, Node):
                    i.print_html(depth+1)
                else:
                    for l in i.splitlines():
                        print(line + setup.indent * ' ' + l)
        line += "".format(self.tag)
        print(line)


def get_args():
    cla = argparse.ArgumentParser(prog='mdconv.py',
                                  description="Convert markdown files to a HTML page",
                                  epilog="Supports leading Metadata blocks")
    cla.add_argument("-t", "--title", type=str, help="Title of the HTML-Document")
    cla.add_argument("-o", "--out", required = False, type=str, help="Output file")
    cla.add_argument("file", type=str, nargs="+", help="Input file")
    return cla.parse_args()


def parse(file):
    html = markdown2.markdown_path(file, extras=["metadata"], tab_width=setup.indent)
    if html.metadata:
        for k, v in html.metadata.items():
            if k.lower() in setup.meta:
                setup.meta[k.lower()] = v
    return html


def output(node, file):
    if not file:
        node.print_html()
        return
    with open(file, 'w', encoding=setup.charset) as f:
        with redirect_stdout(f):
            print('')
            node.print_html()


def main():
    cli_args = get_args()
    # warn user before we overwrite a file
    if (cli_args.out and exists(cli_args.out) and
        not messagebox.askokcancel('Mardown Converter',
                                   'Overwrite {0}'.format(cli_args.out),
                                   icon='warning')):
        exit(2)

    body = Node('body')
    for i in cli_args.file:
        body.add_content(Node('article', content=[parse(i), Node('br')]))

    head = Node('head')
    head.add_content(Node('meta', attributes={'charset': setup.charset}))
    if cli_args.title != None:
        setup.meta['title'] = cli_args.title
    head.add_content(Node("title", content=[setup.meta['title']]))
    del setup.meta['title']
    for n, c in setup.meta.items():
        if c:
            head.add_content(Node('meta', attributes={'name': n, 'content': c}))

    page = Node('html', content=[head, body])

    output(page, cli_args.out)


if __name__ == "__main__":
    main()

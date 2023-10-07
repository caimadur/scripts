#!/usr/bin/env python

import argparse, markdown2
from datetime import date
from contextlib import redirect_stdout
from os.path import exists
from tkinter import messagebox


class Setup:
    """Keep your global namespace clean!"""
    indent = 4
    metadata = {'title': 'Untitled',
                'charset': 'utf-8',
                'viewport': 'width=device-width, initial-scale=1.0',
                'date': str(date.today()),
                'author': 'anonymous',
                'copyright': None}
setup=Setup()


class Node:
    """Class for HTML nodes"""
    def __init__(self, content, preamble, epilog):
        self.content = content
        self.preamble = preamble
        self.epilog = epilog

    def add_content(self, c):
        self.content.append(c)

    def print_html(self, depth=0):
        ind = depth * setup.indent * " "
        print(ind + self.preamble)
        for i in self.content:
            i.print_html(depth + 1)
        print(ind + self.epilog)

class Leaf:
    """HTML nodes that have no children"""
    def __init__(self, content):
        self.content = content

    def print_html(self, depth):
        ind = depth * setup.indent * " "
        for i in self.content.splitlines():
            print(ind + i)


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
    att = ''
    if html.metadata != None:
        for i in html.metadata.keys():
            if i.lower() in setup.metadata:
                setup.metadata[i.lower()] = html.metadata[i]
            if i.lower() in ('class', 'id', 'title'):
                att += '{0}="{1}" '.format(i.lower(), html.metadata[i])
    return '<article ' + att + '>\n' + html + '\n</article>'


def meta(head):
    head.add_content(Leaf('<meta charset="{0}">'.format(setup.metadata['charset'])))
    del setup.metadata['charset']
    head.add_content(Leaf('<title>{0}</title>'.format(setup.metadata['title'])))
    del setup.metadata['title']
    for i in setup.metadata.keys():
        if setup.metadata[i] != None:
            line=Leaf('<meta name="{0}" content="{1}">'.format(i, setup.metadata[i]))
            head.add_content(line)



def main():
    cli_args = get_args()

    body = Node([], "<body>", "</body>")
    for article in cli_args.file:
        body.add_content(Leaf(parse(article)))

    if cli_args.title != None:
        setup.metadata[title] = cli_args.title

    head = Node([], "<head>", "</head>")
    meta(head)

    page = Node([head, body], '<!DOCTYPE html>\n<html>', '</html>')

    if cli_args.out != None:
        # dialog doesn't look nice, but we get attention
        if (exists(cli_args.out) and
            messagebox.askokcancel('Markdown Converter',
                                   'Overwrite existing file {0}?'.format(cli_args.out),
                                   icon='warning') == False):
            exit(2)
        with open(cli_args.out, 'w') as out:
            with redirect_stdout(out):
                page.print_html()
    else:
        page.print_html()



if __name__ == "__main__":
    main()

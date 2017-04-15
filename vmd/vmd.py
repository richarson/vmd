#!/usr/bin/env python3
from styles import *
from elements import *
from writer import *
from renderer import Renderer
import default_formatters
import sys
from parser import Parser
from config import Config
import logging
import os
import re
import argparse


def build_render(writer, config):
    renderer = Renderer(writer)
    renderer.formatters['Paragraph'] = default_formatters.ParagraphFormatter(config)
    renderer.formatters['Heading'] = default_formatters.HeadingFormatter(config)
    renderer.formatters['Strong'] = default_formatters.StrongFormatter(config)
    renderer.formatters['Emphasis'] = default_formatters.EmphasisFormatter(config)
    renderer.formatters['InlineCode'] = default_formatters.InlineCodeFormatter(config)
    renderer.formatters['Link'] = default_formatters.AppendLinkFormatter(config)
    renderer.formatters['List'] = default_formatters.ListFormatter()
    renderer.formatters['ListItem'] = default_formatters.ListItemFormatter(config)
    renderer.formatters['OrderedList'] = 'List'
    renderer.formatters['OrderedListItem'] = default_formatters.OrderedListItemFormatter(config)
    renderer.formatters['HorizontalRule'] = default_formatters.HorizontalRuleFormatter(config)
    renderer.formatters['CodeBlock'] = default_formatters.CodeBlockFormatter(config)

    return renderer


def load_config():
    themes_directory = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'themes')

    theme = os.path.join(themes_directory, 'default')

    if 'VMD_THEME' in os.environ:
        if re.search('^[a-zA-Z_\-0-9]+$', os.environ['VMD_THEME']):
            theme = os.path.join(themes_directory, os.environ['VMD_THEME'])
        else:
            theme = os.environ['VMD_THEME']

    config = Config([theme, '~/.vmdrc'])

    config.load()

    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0, dest='verbosity')

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('file', nargs='?', metavar='FILE', help='The path to the markdown file')
    input_group.add_argument('--stdin', dest='stdin', action='store_true', help='Read Markdown from stdin')

    args = parser.parse_args()

    if args.verbosity != 0:
        logging_level = 10 * max(0, 3 - args.verbosity)

        logging.basicConfig(level=logging_level)

    mdparser = Parser()

    config = load_config()

    writer = DisplayWriter(sys.stdout)

    renderer = build_render(writer, config)

    if args.stdin:
        doc = mdparser.parse(sys.stdin.read())
    elif args.file is not None:
        with open(args.file) as f:
            doc = mdparser.parse(f.read())
    else:
        parser.print_help()
        sys.exit(1)

    renderer.render_document(doc)

    sys.stdout.write('\n')
    sys.stdout.flush()
    sys.stdout.close()

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""Additional pyflakes"""
# :copyright: (c) 2012 by Ask Solem.
# :license: BSD, see LICENSE for more details.

from __future__ import absolute_import

VERSION = (1, 0, 0)
__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Ask Solem"
__contact__ = "ask@celeryproject.org"
__homepage__ = "http://github.com/ask/flakeplus"
__docformat__ = "restructuredtext"

# -eof meta-

import os
import pprint
import re
import sys

from collections import defaultdict
from itertools import starmap
from optparse import OptionParser, make_option as Option
from unipath import Path

EX_USAGE = getattr(os, "EX_USAGE", 0x40)

RE_COMMENT = r'^\s*\#'
RE_NOQA = r'.+?\#\s+noqa+'
RE_MULTILINE_COMMENT_O = r'^\s*(?:\'\'\'|""").+?(?:\'\'\'|""")'
RE_MULTILINE_COMMENT_S = r'^\s*(?:\'\'\'|""")'
RE_MULTILINE_COMMENT_E = r'(?:^|.+?)(?:\'\'\'|""")'
RE_WITH = r'(?:^|\s+)with\s+'
RE_WITH_IMPORT = r'''from\s+ __future__\s+ import\s+ with_statement'''
RE_PRINT = r'''(?:^|\s+)print\((?:"|')(?:\W+?)?[A-Z0-9:]{2,}'''
RE_ABS_IMPORT = r'''from\s+ __future__\s+ import\s+ absolute_import'''

acc = defaultdict(lambda: {"abs": False, "print": False})

__version__ = "1.0.0"


def compile(regex):
    return re.compile(regex, re.VERBOSE)


class FlakePP(object):
    re_comment = compile(RE_COMMENT)
    re_ml_comment_o = compile(RE_MULTILINE_COMMENT_O)
    re_ml_comment_s = compile(RE_MULTILINE_COMMENT_S)
    re_ml_comment_e = compile(RE_MULTILINE_COMMENT_E)
    re_abs_import = compile(RE_ABS_IMPORT)
    re_print = compile(RE_PRINT)
    re_with_import = compile(RE_WITH_IMPORT)
    re_with = compile(RE_WITH)
    re_noqa = compile(RE_NOQA)
    map = {"abs": False, "print": False,
            "with": False, "with-used": False}

    def __init__(self, verbose=False, use_26=False, quiet=False):
        self.verbose = verbose  # XXX unused
        self.quiet = quiet
        self.use_26 = use_26
        self.steps = (("abs", self.re_abs_import),
                      ("with", self.re_with_import),
                      ("with-used", self.re_with),
                      ("print", self.re_print))

    def analyze_fh(self, fh):
        steps = self.steps
        filename = fh.name
        acc = dict(self.map)
        index = 0
        errors = [0]

        def error(fmt, **kwargs):
            errors[0] += 1
            self.announce(fmt, **dict(kwargs, filename=filename))

        for index, line in enumerate(self.strip_comments(fh)):
            for key, pattern in self.steps:
                if pattern.match(line):
                    acc[key] = True
        if index:
            if not acc["abs"]:
                error("%(filename)s: missing abs import")
            if not self.use_26 and acc["with-used"] and not acc["with"]:
                error("%(filename)s: missing with import")
            if acc["print"]:
                error("%(filename)s: left over print statement")

        return filename, errors[0], acc

    def analyze_file(self, filename):
        with open(filename) as fh:
            return self.analyze_fh(fh)

    def analyze_tree(self, dir):
        for dirpath, _, filenames in os.walk(dir):
            for path in (Path(dirpath, f) for f in filenames):
                if path.endswith(".py"):
                    yield self.analyze_file(path)

    def analyze(self, *paths):
        for path in map(Path, paths):
            if path.isdir():
                for res in self.analyze_tree(path):
                    yield res
            else:
                yield self.analyze_file(path)

    def strip_comments(self, fh):
        re_comment = self.re_comment
        re_ml_comment_o = self.re_ml_comment_o
        re_ml_comment_s = self.re_ml_comment_s
        re_ml_comment_e = self.re_ml_comment_e
        re_noqa = self.re_noqa
        in_ml = False

        for line in fh.readlines():
            if in_ml:
                if re_ml_comment_e.match(line):
                    in_ml = False
            else:
                if re_noqa.match(line) or re_ml_comment_o.match(line):
                    pass
                elif re_ml_comment_s.match(line):
                    in_ml = True
                elif re_comment.match(line):
                    pass
                else:
                    yield line

    def announce(self, fmt, **kwargs):
        if not self.quiet:
            sys.stderr.write((fmt + "\n") % kwargs)



class Command(object):
    FlakePP = FlakePP
    Parser = OptionParser

    args = 'dir1 .. dirN'
    version = __version__

    def run(self, *files, **kwargs):
        exitcode = 0
        for _, errors, _ in self.FlakePP(**kwargs).analyze(*files):
            if errors:
                exitcode = 1
        return exitcode

    def get_options(self):
        return (
            Option("--2.6",
                   default=False, action="store_true", dest="use_26",
                   help="Specify support of Python 2.6 and up"),
            Option("--verbose", "-v",
                   default=False, action="store_true", dest="verbose",
                   help="Show more output."),
            Option("--quiet", "-q",
                    default=False, action="store_true", dest="quiet",
                    help="Don't show any output"),
        )

    def usage(self):
        return "%%prog [options] %s" % (self.args, )

    def die(self, msg):
        self.usage()
        sys.stderr.write("%s\n" % msg)
        return EX_USAGE

    def expanduser(self, value):
        if isinstance(value, basestring):
            return os.path.expanduser(value)
        return value

    def handle_argv(self, prog_name, argv):
        options, args = self.parse_options(prog_name, argv)
        options = dict((k, self.expanduser(v))
                            for k, v in vars(options).iteritems()
                                if not k.startswith("_"))
        argv = map(self.expanduser, argv)
        if not argv:
            return self.die("No input files/directories")
        return self.run(*args, **options)

    def parse_options(self, prog_name, argv):
        parser = self.Parser(prog=prog_name,
                             usage=self.usage(),
                             version=self.version,
                             option_list=self.get_options())
        return parser.parse_args(argv)

    def execute_from_commandline(self, argv=None):
        if argv is None:
            argv = list(sys.argv)
        prog_name = os.path.basename(argv[0])
        return self.handle_argv(prog_name, argv[1:])


def main(argv=sys.argv):
    sys.exit(Command().execute_from_commandline(argv))


if __name__ == "__main__":
    main()

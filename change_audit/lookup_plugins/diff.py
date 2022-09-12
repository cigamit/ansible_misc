# -*- coding: utf-8 -*-
# Copyright 2020 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""
The diff lookup plugin
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = """
    name: diff
    author: Jimmy Conner
    version_added: "1.0.0"
    short_description: Return diff of 2 strings
    description:
      - Return diff of 2 strings
    options:
      before:
        description:
          - The text before the change
        type: str
        required: True
      after:
        description:
          - The text after the change
        type: str
        required: True
      header:
        description:
          - The filename
        type: str
    notes:
"""

EXAMPLES = r"""

#### Simple examples

"""

RETURN = """
  _raw:
    description:
      - The diff
"""
import re

from importlib import import_module

from ansible.plugins.callback import CallbackBase

from ansible.errors import AnsibleLookupError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

from collections.abc import MutableMapping
import difflib
from ansible import constants as C
from ansible.utils.color import stringc

#from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
#    AnsibleArgSpecValidator,
#)

display = Display()

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        res = []

        if isinstance(terms, list):
            keys = [
                "before",
                "after",
                "header",
            ]
            terms = dict(zip(keys, terms))
        terms.update(kwargs)

        self.debug = True
        diff = FactDiff(terms, variables, self.debug);

        ret = diff.diff()
        display.vvvv("------------------------------------")
        display.vvvv(ret)
        display.vvvv("------------------------------------")

        #display.vvvv(res);

        #display.vvvv("DIFF: %s" % ret)
        res.append(ret)
        return res

    
class FactDiffBase:
    def __init__(self, task_args, task_vars, debug):
        self._debug = debug
        self._task_args = task_args
        self._task_vars = task_vars

class FactDiff(FactDiffBase):
    def _check_valid_regexes(self):
        if self._skip_lines:
            self._debug("Checking regex in 'split_lines' for validity")
            for idx, regex in enumerate(self._skip_lines):
                try:
                    self._skip_lines[idx] = re.compile(regex)
                except re.error as exc:
                    msg = "The regex '{regex}', is not valid. The error was {err}.".format(
                        regex=regex,
                        err=str(exc),
                    )
                    self._errors.append(msg)

    def _xform(self):
        if self._skip_lines:
            if isinstance(self._before, str):
                self._debug("'before' is a string, splitting lines")
                self._before = self._before.splitlines()
            if isinstance(self._after, str):
                self._debug("'after' is a string, splitting lines")
                self._after = self._after.splitlines()
            self._before = [
                line
                for line in self._before
                if not any(regex.match(str(line)) for regex in self._skip_lines)
            ]
            self._after = [
                line
                for line in self._after
                if not any(regex.match(str(line)) for regex in self._skip_lines)
            ]
        if isinstance(self._before, list):
            self._debug("'before' is a list, joining with \n")
            self._before = "\n".join(map(str, self._before)) + "\n"
        if isinstance(self._after, list):
            self._debug("'after' is a list, joining with \n")
            self._after = "\n".join(map(str, self._after)) + "\n"

    def diff(self):
        self._after = self._task_args["after"]
        self._before = self._task_args["before"]
        self._header = self._task_args["header"]
        self._errors = []
        self._skip_lines = False #self._task_args["plugin"]["vars"].get("skip_lines")
        self._check_valid_regexes()
        if self._errors:
            return {"errors": " ".join(self._errors)}
        self._xform()
        diff = self._get_diff({"before": self._before, "after": self._after, "header": self._header})
        return diff
    
    def _get_diff(self, difflist):

        if not isinstance(difflist, list):
            difflist = [difflist]

        ret = []
        for diff in difflist:
            if 'dst_binary' in diff:
                ret.append(u"diff skipped: destination file appears to be binary\n")
            if 'src_binary' in diff:
                ret.append(u"diff skipped: source file appears to be binary\n")
            if 'dst_larger' in diff:
                ret.append(u"diff skipped: destination file size is greater than %d\n" % diff['dst_larger'])
            if 'src_larger' in diff:
                ret.append(u"diff skipped: source file size is greater than %d\n" % diff['src_larger'])
            if 'before' in diff and 'after' in diff:
                # format complex structures into 'files'
                for x in ['before', 'after']:
                    if isinstance(diff[x], MutableMapping):
                        diff[x] = self._serialize_diff(diff[x])
                    elif diff[x] is None:
                        diff[x] = ''
                if 'header' in diff:
                    before_header = u"before: %s" % diff['header']
                else:
                    before_header = u'before'
                if 'header' in diff:
                    after_header = u"after: %s" % diff['header']
                else:
                    after_header = u'after'
                before_lines = diff['before'].splitlines(True)
                after_lines = diff['after'].splitlines(True)
                if before_lines and not before_lines[-1].endswith(u'\n'):
                    before_lines[-1] += u'\n\\ No newline at end of file\n'
                if after_lines and not after_lines[-1].endswith('\n'):
                    after_lines[-1] += u'\n\\ No newline at end of file\n'
                differ = difflib.unified_diff(before_lines,
                                              after_lines,
                                              fromfile=before_header,
                                              tofile=after_header,
                                              fromfiledate=u'',
                                              tofiledate=u'',
                                              n=C.DIFF_CONTEXT)
                difflines = list(differ)
                has_diff = False
                for line in difflines:
                    has_diff = True
                    if line.startswith(u'+'):
#                        line = stringc(line, C.COLOR_DIFF_ADD)
                        line = "<font color=green>" + line + "</font>"
                    elif line.startswith(u'-'):
#                        line = stringc(line, C.COLOR_DIFF_REMOVE)
                        line = "<font color=red>" + line + "</font>"
                    elif line.startswith(u'@@'):
#                        line = stringc(line, C.COLOR_DIFF_LINES)
                        line = "<font color=cyan>" + line + "</font>"
                    ret.append(line)
                if has_diff:
                    ret.append('\n')
            if 'prepared' in diff:
                ret.append(diff['prepared'])
        return u''.join(ret)

    def _serialize_diff(self, diff):
        try:
            result_format = self.get_option('result_format')
        except KeyError:
            # Callback does not declare result_format nor extend result_format_callback
            result_format = 'json'

        try:
            pretty_results = self.get_option('pretty_results')
        except KeyError:
            # Callback does not declare pretty_results nor extend result_format_callback
            pretty_results = None

        if result_format == 'json':
            return json.dumps(diff, sort_keys=True, indent=4, separators=(u',', u': ')) + u'\n'
        elif result_format == 'yaml':
            # None is a sentinel in this case that indicates default behavior
            # default behavior for yaml is to prettify results
            lossy = pretty_results in (None, True)
            return '%s\n' % textwrap.indent(
                yaml.dump(
                    diff,
                    allow_unicode=True,
                    Dumper=_AnsibleCallbackDumper(lossy=lossy),
                    default_flow_style=False,
                    indent=4,
                    # sort_keys=sort_keys  # This requires PyYAML>=5.1
                ),
                '    '
            )

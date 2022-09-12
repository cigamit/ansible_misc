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
          - Header String
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

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase

from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)

class LookupModule(LookupBase):
    def _debug(self, msg):
        """Output text using ansible's display
        :param msg: The message
        :type msg: str
        """
        msg = "<{phost}> [fact_diff][{plugin}] {msg}".format(
            phost="host", #self._playhost,
            plugin="diff", #self._plugin,
            msg=msg,
        )
        self._display.vvvv(msg)
    def run(self, terms, variables, **kwargs):
        if isinstance(terms, list):
            keys = ["before", "after", "header"]
            terms = dict(zip(keys, terms))
        terms.update(kwargs)

        schema = [v for k, v in globals().items() if k.lower() == "documentation"]
        aav = AnsibleArgSpecValidator(data=terms, schema=schema[0], name="diff")
        valid, errors, updated_data = aav.validate()
        if not valid:
            raise AnsibleLookupError(errors)
        updated_data["wantlist"] = False
        self.debug = True
        
        diff = FactDiff(terms, variables, self.debug);
        res = diff.diff()
        
        return res.diff

    
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
        self._errors = []
        self._skip_lines = False #self._task_args["plugin"]["vars"].get("skip_lines")
        self._check_valid_regexes()
        if self._errors:
            return {"errors": " ".join(self._errors)}
        self._xform()
        diff = CallbackBase()._get_diff({"before": self._before, "after": self._after})
        return {"diff": diff}
    
    def _debug(self, msg):
        """Output text using ansible's display
        :param msg: The message
        :type msg: str
        """
        msg = "<{phost}> [fact_diff][{plugin}] {msg}".format(
            phost="host", #self._playhost,
            plugin="diff", #self._plugin,
            msg=msg,
        )
        self._display.vvv(msg)

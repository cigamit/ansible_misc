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

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase

from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)

class LookupModule(LookupBase):
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

        
        
        return res

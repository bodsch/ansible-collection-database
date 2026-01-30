# python 3 headers, required if submitting to Ansible
from __future__ import absolute_import, print_function

__metaclass__ = type

import os

from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """ """

    def filters(self):
        return {
            "is_absolute_path": self.is_absolute_path,
        }

    def is_absolute_path(self, data):
        """
        Plattformunabhängige Prüfung eines absoluten Pfads.

        :param path: Der zu prüfende Pfadstring
        :return: True für absoluten Pfad, False für relativen Pfad
        """
        display.vv(f"is_absolute_path({data})")

        return os.path.isabs(data)

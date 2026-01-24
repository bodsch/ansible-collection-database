# python 3 headers, required if submitting to Ansible


from __future__ import absolute_import, print_function

__metaclass__ = type

# import os
# import re

# try:
#     from collections.abc import Mapping
# except ImportError:  # pragma: no cover
#     from collections import Mapping

# import json
from ansible.utils.display import Display

# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html
# https://blog.oddbit.com/post/2019-04-25-writing-ansible-filter-plugins/

display = Display()


class FilterModule(object):
    """ """

    def filters(self):
        return {
            "pg_validate_connection_type": self.validate_connection_type,
        }

    def validate_connection_type(self, data):
        """
        - "local" is a Unix-domain socket
        - "host" is a TCP/IP socket (encrypted or not)
        - "hostssl" is a TCP/IP socket that is SSL-encrypted
        - "hostnossl" is a TCP/IP socket that is not SSL-encrypted
        - "hostgssenc" is a TCP/IP socket that is GSSAPI-encrypted
        - "hostnogssenc" is a TCP/IP socket that is not GSSAPI-encrypted
        """
        display.vv(f"validate_connection_type({data})")

        valid = ["local", "host", "hostssl", "hostnossl", "hostgssenc", "hostnogssenc"]

        if data in valid:
            return True
        else:
            return False

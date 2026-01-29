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
            "pg_validate_password_encryption": self.validate_password_encryption,
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

    def validate_password_encryption(self, data):
        """
        https://www.postgresql.org/docs/current/auth-password.html

        # METHOD can be
        # "trust", "reject", "md5", "password", "scram-sha-256",
        # "gss", "sspi", "ident", "peer", "pam", "ldap", "radius" or "cert".
        # Note that "password" sends passwords in clear text; "md5" or
        # "scram-sha-256" are preferred since they send encrypted passwords.
        """
        display.vv(f"validate_password_encryption({data})")

        valid = [
            "trust",
            "reject",
            "md5",
            "password",
            "scram-sha-256",
            "gss",
            "sspi",
            "ident",
            "peer",
            "pam",
            "ldap",
            "radius",
            "cert",
        ]

        if data in valid:
            return True
        else:
            return False

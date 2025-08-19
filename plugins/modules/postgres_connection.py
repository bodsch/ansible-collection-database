#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2020-2024, Bodo Schulz <bodo@boone-schulz.de>
# Apache (see LICENSE or https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
import os
import json
import hashlib

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.database.plugins.module_utils.postgres.settings_reader import PgSettingsReader




class PostgresConnection:
    """
    """
    module = None

    def __init__(self, module):
        """
        """
        self.module = module

        # self._occ = module.get_bin_path('console', False)

        self.command = module.params.get("command")

    def run(self):
        """
        """
        self.module.log(msg=f"PostgresConnection::run()")

        reader = PgSettingsReader(
            module=self.module,
            keys=["listen_addresses", "port", "unix_socket_directories"])
            # keys=args.keys,
            # dbname=args.db,
            # user=args.user,
            # connect_timeout=args.timeout,
            # conf_path=args.conf,
        # )

        # config = reader.parse_postgresql_conf()
        # self.module.log(msg=f"config: {json.dumps(config, ensure_ascii=False)}")

        data = reader.read()
        self.module.log(msg=f"data: {json.dumps(data, ensure_ascii=False)}")

        return dict(
            failed=False,
            changed=False,
            msg="failed"
        )

def main():
    """
    """
    specs = dict()

    module = AnsibleModule(
        argument_spec=specs,
        supports_check_mode=False,
    )

    c = PostgresConnection(module)
    result = c.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()


"""
sudo -u postgres psql -XAt -c "
SELECT jsonb_strip_nulls(
  jsonb_build_object(
    'listen_addresses', current_setting('listen_addresses', true),
    'port', current_setting('port', true),
    'unix_socket_directories', current_setting('unix_socket_directories', true)
  )
)::text;"
"""

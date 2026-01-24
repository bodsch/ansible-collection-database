#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2020-2024, Bodo Schulz <bodo@boone-schulz.de>
# Apache (see LICENSE or https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

import hashlib
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.database.plugins.module_utils.postgres.settings_reader import (
    PgSettingsReader,
)


class PostgresConnection:
    """ """

    def __init__(self, module: Any):
        """ """
        self.module = module

        # self._occ = module.get_bin_path('console', False)

        self.command = module.params.get("command")

    def run(self):
        """ """
        self.module.log(msg=f"PostgresConnection::run()")

        reader = PgSettingsReader(
            module=self.module,
            keys=["listen_addresses", "port", "unix_socket_directories"],
        )
        # keys=args.keys,
        # dbname=args.db,
        # user=args.user,
        # connect_timeout=args.timeout,
        # conf_path=args.conf,
        # )

        # config = reader.parse_postgresql_conf()
        # self.module.log(msg=f"config: {json.dumps(config, ensure_ascii=False)}")

        # self.module.log("--------------------------------")
        data = reader.read()
        # self.module.log(f" type {type(data)}")
        # self.module.log(f" {data}")
        # self.module.log("--------------------------------")
        # self.module.log(f"data: {json.dumps(data, ensure_ascii=False)}")

        if isinstance(data, dict):
            # {"listen_addresses": "127.0.0.1", "port": "5432", "unix_socket_directories": "/var/run/postgresql"}
            _address = data.get("listen_addresses", "127.0.0.1")
            _port = data.get("port", None)
            _socket_dirs = data.get("unix_socket_directories", None)

            _sockets = self.find_socket_files(_socket_dirs)

            result = {
                "listen": {"address": _address, "port": _port},
                "socket": {"directories": _socket_dirs},
            }

            return {"failed": False, "changed": False, "connections": result}

        return dict(failed=False, changed=False, msg="failed")

    def find_socket_files(self, directories: List) -> List:
        """ """
        result: List = []

        return result


def main():
    """ """
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
if __name__ == "__main__":
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

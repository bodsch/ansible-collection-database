from __future__ import annotations, unicode_literals

import os

from helper.molecule import get_vars, local_facts, pp_json

# --- tests -----------------------------------------------------------------


def test_data_directory(host, get_vars):
    """
    configured datadir
    """
    directory = get_vars.get("mariadb_config_mysqld", {}).get(
        "datadir", "/var/lib/mysql"
    )
    user = "mysql"

    dir = host.file(directory)
    assert not dir.is_directory

from __future__ import annotations, unicode_literals

import os

from helper.molecule import get_vars, local_facts, pp_json

# --- tests -----------------------------------------------------------------


def test_files(host):
    """ """
    files = [
        "/lib/systemd/system/mariadb-backup.service",
        "/lib/systemd/system/mariadb-backup.timer",
    ]

    for _file in files:
        f = host.file(_file)
        assert f.is_file

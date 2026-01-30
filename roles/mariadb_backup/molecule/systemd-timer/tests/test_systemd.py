from __future__ import annotations, unicode_literals

import os

from helper.molecule import get_vars, local_facts, pp_json

# --- tests -----------------------------------------------------------------


@pytest.mark.parametrize(
    "files",
    [
        "/lib/systemd/system/mariadb-backup.service",
        "/lib/systemd/system/mariadb-backup.timer",
    ],
)
def test_files(host, files):
    f = host.file(files)
    assert f.is_file

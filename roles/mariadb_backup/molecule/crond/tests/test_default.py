from __future__ import annotations, unicode_literals

import os

from helper.molecule import get_vars, local_facts, pp_json

# --- tests -----------------------------------------------------------------


@pytest.mark.parametrize("dirs", ["/etc/mariadb_backup"])
def test_directories(host, dirs):
    d = host.file(dirs)
    assert d.is_directory
    assert d.exists


@pytest.mark.parametrize(
    "files",
    [
        "/etc/mariadb_backup/mariadb_backup.yml",
        "/usr/local/bin/mariadb_backup.py",
    ],
)
def test_files(host, files):
    f = host.file(files)
    assert f.exists
    assert f.is_file

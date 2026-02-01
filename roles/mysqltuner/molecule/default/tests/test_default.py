from __future__ import annotations, unicode_literals

import os

from helper.molecule import get_vars, local_facts, pp_json

# --- tests -----------------------------------------------------------------


def test_directories(host):
    """ """
    directories = ["/usr/local/opt/mysqltuner"]

    for dirs in directories:
        d = host.file(dirs)
        assert d.is_directory


def test_files(host):
    """ """
    files = [
        "/usr/local/bin/mysqltuner.pl",
        "/usr/local/bin/basic_passwords.txt",
        "/usr/local/bin/vulnerabilities.csv",
    ]

    for _file in files:
        f = host.file(_file)
        assert f.is_file
